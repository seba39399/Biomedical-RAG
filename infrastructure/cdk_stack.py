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

# 📌 Calculamos la raíz real del proyecto (un nivel arriba de /infrastructure)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_PATH = os.path.join(BASE_DIR, "backend")
FRONTEND_PATH = os.path.join(BASE_DIR, "frontend")


class ChatbotRagStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Capturamos la API KEY asegurando que no llegue un string vacío de AWS
        groq_key = os.getenv("GROQ_API_KEY")
        if not groq_key:
            # Esto previene que despliegues una tarea rota en Fargate
            print("⚠️ WARNING: GROQ_API_KEY no detectada en las variables de entorno del host local.")

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
                # 🔥 SOLUCIÓN AQUÍ: Pasamos groq_key como build_arg para que el Dockerfile la capture
                image=ecs.ContainerImage.from_asset(
                    BACKEND_PATH,
                    build_args={
                        "GROQ_API_KEY": groq_key or ""
                    }
                ),
                container_port=8000,
                environment={
                    "PROJECT_NAME": "Biomedical RAG OPs (AWS Live)",
                    "GROQ_API_KEY": groq_key or "",
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
                image=ecs.ContainerImage.from_asset(FRONTEND_PATH),
                container_port=8501,
                environment={"BACKEND_URL": backend_url, "API_URL": backend_url},
            ),
            public_load_balancer=True,
        )
