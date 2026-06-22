import os

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
    aws_ecs_patterns as ecs_patterns,
)
from constructs import Construct

# 📌 AQUÍ ESTÁ EL TRUCO: Calculamos la raíz real del proyecto (un nivel arriba de /infrastructure)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_PATH = os.path.join(BASE_DIR, "backend")
FRONTEND_PATH = os.path.join(BASE_DIR, "frontend")


class ChatbotRagStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. Red virtual (VPC) compartida para ambos servicios
        vpc = ec2.Vpc(self, "ChatbotRagVpc", max_azs=2)

        # 2. Clúster de ECS único
        cluster = ecs.Cluster(self, "ChatbotRagCluster", vpc=vpc)

        # 3. SERVICIO 1: Backend (FastAPI)
        self.backend_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "ChatbotRagBackendService",
            cluster=cluster,
            cpu=512,
            memory_limit_mib=1024,
            desired_count=1,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                # 🔥 Usamos la ruta absoluta dinámica calculada arriba
                image=ecs.ContainerImage.from_asset(BACKEND_PATH),
                container_port=8000,
                environment={
                    "PROJECT_NAME": "Biomedical RAG OPs (AWS Live)",
                    "GROQ_API_KEY": os.getenv("GROQ_API_KEY", ""),
                },
            ),
            public_load_balancer=True,
        )

        # Ajustamos el health check del backend para que apunte a la raíz "/"
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
                # 🔥 Usamos la ruta absoluta dinámica calculada arriba
                image=ecs.ContainerImage.from_asset(FRONTEND_PATH),
                container_port=8501,
                environment={"BACKEND_URL": backend_url, "API_URL": backend_url},
            ),
            public_load_balancer=True,
        )
