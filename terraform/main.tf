terraform {
  required_version = ">= 1.6"
  required_providers { kubernetes = { source = "hashicorp/kubernetes", version = "~> 2.35" } }
}
provider "kubernetes" { config_path = var.kubeconfig }
variable "kubeconfig" { type=string default=null nullable=true }
variable "namespace" { type=string default="ai-platform" }
variable "replicas" { type=number default=2 }
variable "image" { type=string default="secure-ai-gateway:0.1.0" }
resource "kubernetes_deployment" "api" {
  metadata { name="secure-ai-gateway" namespace=var.namespace labels={app="secure-ai-gateway"} }
  spec { replicas=var.replicas selector { match_labels={app="secure-ai-gateway"} } template {
    metadata { labels={app="secure-ai-gateway"} }
    spec {
      security_context {
        run_as_non_root=true
        run_as_user=10001
        run_as_group=10001
        seccomp_profile { type="RuntimeDefault" }
      }
      container {
        name="api"
        image=var.image
        port {container_port=8000}
        security_context {
          allow_privilege_escalation=false
          read_only_root_filesystem=true
          capabilities { drop=["ALL"] }
          seccomp_profile { type="RuntimeDefault" }
        }
        resources { requests={cpu="100m",memory="128Mi"} limits={cpu="500m",memory="512Mi"} }
        readiness_probe { http_get {path="/health/ready" port=8000} }
        liveness_probe { http_get {path="/health/live" port=8000} }
      }
    }
  }}
}
resource "kubernetes_service" "api" {
 metadata {name="secure-ai-gateway" namespace=var.namespace}
 spec { selector={app="secure-ai-gateway"} port {port=80 target_port=8000} }
}
output "service_name" { value=kubernetes_service.api.metadata[0].name }
