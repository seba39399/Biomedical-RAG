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


class ChatbotRagStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # 1. Red virtual (VPC) compartida para ambos servicios
        vpc = ec2.Vpc(self, "ChatbotRagVpc", max_azs=2)

        # 2. Clúster de ECS único
        cluster = ecs.Cluster(self, "ChatbotRagCluster", vpc=vpc)

        # 3. SERVICIO 1: Backend (FastAPI) compitándose desde la carpeta local
        self.backend_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "ChatbotRagBackendService",
            cluster=cluster,
            cpu=512,
            memory_limit_mib=1024,
            desired_count=1,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                # 🔥 CAMBIO CLAVE: Cambiamos registry por asset para que compile tu código actual
                image=ecs.ContainerImage.from_asset("./backend"),
                container_port=8000,
                environment={
                    "PROJECT_NAME": "Biomedical RAG OPs (AWS Live)",
                    "GROQ_API_KEY": os.getenv("GROQ_API_KEY", ""),
                }
            ),
            public_load_balancer=True
        )

        # Ajustamos el health check del backend para que apunte a la raíz "/"
        self.backend_service.target_group.configure_health_check(
            path="/"
        )

        # 4. SERVICIO 2: Frontend (Streamlit)
        # Obtenemos la URL del backend dinámicamente (limpia, sin /api/v1 al final)
        backend_url = f"http://{self.backend_service.load_balancer.load_balancer_dns_name}"

        self.frontend_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "ChatbotRagFrontendService",
            cluster=cluster,
            cpu=512,
            memory_limit_mib=1024,
            desired_count=1,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                # 🔥 CAMBIO CLAVE: Compila la carpeta frontend local con los requests corregidos
                image=ecs.ContainerImage.from_asset("./frontend"),
                container_port=8501,  # Puerto nativo en el que corre Streamlit
                environment={
                    # Aquí ocurre la magia: Streamlit unirá esto con /api/v1/query o /api/v1/ingest
                    "BACKEND_URL": backend_url,
                    "API_URL": backend_url
                }
            ),
            public_load_balancer=True  # Nos genera OTRA URL pública para el cliente
        )