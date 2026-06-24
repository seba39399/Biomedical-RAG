import os

# 🚨 IMPORTACIÓN CORRECTA PARA CDK V2:
import aws_cdk.aws_ecs_patterns as ecs_patterns
from aws_cdk import (
    Stack,
)
from aws_cdk import (
    aws_ec2 as ec2,
)
from aws_cdk import (
    aws_ecs as ecs,
)
from aws_cdk import (
    aws_secretsmanager as secretsmanager,
)
from constructs import Construct

# 📌 Calculamos la raíz real del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_PATH = os.path.join(BASE_DIR, "backend")
FRONTEND_PATH = os.path.join(BASE_DIR, "frontend")


class ChatbotRagStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. Red virtual (VPC) y Clúster de ECS único
        vpc = ec2.Vpc(self, "ChatbotRagVpc", max_azs=2)
        cluster = ecs.Cluster(self, "ChatbotRagCluster", vpc=vpc)

        # 2. TRAEMOS EL SECRETO: Buscamos en AWS el secreto que creaste en la web
        groq_secret_aws = secretsmanager.Secret.from_secret_name_v2(
            self, "ImportedGroqSecret", "prod/chatbot/groq"
        )

        # Mapeamos la clave interna del JSON del secreto para ECS Fargate
        fargate_secret = ecs.Secret.from_secrets_manager(
            groq_secret_aws, "GROQ_API_KEY"
        )

        # 3. SERVICIO 1: Backend (FastAPI)
        self.backend_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "ChatbotRagBackendService",
            cluster=cluster,
            cpu=512,
            memory_limit_mib=1024,
            desired_count=1,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_asset(BACKEND_PATH),
                container_port=8000,
                environment={
                    "PROJECT_NAME": "Biomedical RAG OPs (AWS Live)",
                },
                # 🚀 INYECCIÓN DINÁMICA: Fargate lee el secreto y lo monta en la RAM del contenedor
                secrets={"GROQ_API_KEY": fargate_secret},
            ),
            public_load_balancer=True,
        )

        # Ajustamos el health check del backend
        self.backend_service.target_group.configure_health_check(path="/")

        # 4. SERVICIO 2: Frontend (Streamlit)
        backend_url = (
            f"http://{self.backend_service.load_balancer.load_balancer_dns_name}"
        )

        self.frontend_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "ChatbotRagFrontendService",
            cluster=cluster,
            cpu=512,
            memory_limit_mib=1024,
            desired_count=1,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_asset(FRONTEND_PATH),
                container_port=8501,
                environment={
                    "BACKEND_URL": backend_url,
                    "API_URL": backend_url,
                },
                # 🚨 Satisface la validación de Pydantic pasándole el mismo secreto seguro
                secrets={"GROQ_API_KEY": fargate_secret},
            ),
            public_load_balancer=True,
        )
