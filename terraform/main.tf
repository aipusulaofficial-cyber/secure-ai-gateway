terraform { required_version = ">= 1.6" }
variable "replicas" { type=number default=2 }
variable "image" { type=string default="secure-ai-gateway:latest" }
output "deployment_contract" { value={image=var.image,replicas=var.replicas} }
