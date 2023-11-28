variable "region" {
  description = "Region for the  Backup plan and Backup Policies"
  default     = "eu-west-1"
}

variable "project_name" {
  description = "nom du projet"
  default     = "topic-leader-backup"
}
variable "name" {
  description = "Name of the sns topic"
  default     = "sns-report-alert"
}
variable "stack_name" {
  description = "Name of the stack"
  default     = "SUPPORT"
}
variable "env" {
  description = "Define the Environment"
  default     = "backup"
}