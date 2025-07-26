variable "subscription_id" {
    type = string
    description = "The Azure subscription ID"
}

variable "location" {
    type = string
    description = "The Azure region to deploy resources"
    default = "Central US"
}

variable "project" {
    type = string
    description = "The name of the project"
    default = "indianpharma"
}

variable "environment" {
    type = string
    description = "The environment to deploy resources"
    default = "dev"
}

variable "tags" {
    type = map(string)
    description = "A map of tags to apply to all resources"
    default = {
        environment = "development"
        date = "jul-2025"
        createdBy = "Terraform"
    }
}

variable "admin_sql_password"{
    type = string
    description = "The password for the SQL administrator"
}

variable "SQL_DRIVER" {
    type = string
}

variable "SQL_SERVER" {
    type = string
}

variable "SQL_DATABASE" {
    type = string
}

variable "SQL_USERNAME" {
    type = string
}

variable "FIREBASE_API_KEY" {
    type = string
}

variable "SECRET_KEY" {
    type = string
}

variable "APPLICATIONINSIGHTS_CONNECTION_STRING" {
    type = string
}

variable "REDIS_CONNECTION_STRING" {
    type = string
}

variable "DOCKER_REGISTRY_SERVER_URL" {
    type = string
}

variable "DOCKER_REGISTRY_SERVER_USERNAME" {
    type = string
}

variable "DOCKER_REGISTRY_SERVER_PASSWORD" {
    type = string
}
