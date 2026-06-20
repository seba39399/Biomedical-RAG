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

        # 1. Crear una red virtual (VPC) aislada y segura en AWS
        vpc = ec2.Vpc(self, "ChatbotRagVpc", max_azs=2)

        # 2. Crear el clúster de ECS donde vivirán los contenedores
        cluster = ecs.Cluster(self, "ChatbotRagCluster", vpc=vpc)

        # 3. Patrón de CDK para levantar Fargate con un Balanceador de Carga
        self.fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "ChatbotRagFargateService",
            cluster=cluster,
            cpu=512,                    # 0.5 vCPU (Económico para pruebas)
            memory_limit_mib=1024,      # 1 GB de RAM
            desired_count=1,            # 1 sola instancia encendida
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                # 🔥 CAMBIO AQUÍ: Jalar directamente desde tu DockerHub público
                image=ecs.ContainerImage.from_registry("seba39399/biomedical-rag-backend:latest"),
                container_port=8000,    # Puerto interno del FastAPI
                environment={
                    "PROJECT_NAME": "Biomedical RAG OPs (AWS Live)",
                }
            ),
            public_load_balancer=True   # Nos genera una URL pública
        )
