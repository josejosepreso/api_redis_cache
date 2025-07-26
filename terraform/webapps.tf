resource "azurerm_service_plan" "sp" {
    name = "sp-${ var.project }-${ var.environment }"
    location = var.location
    resource_group_name = azurerm_resource_group.rg.name
    sku_name = "B1"
    os_type = "Linux"

    tags = var.tags
}

resource "azurerm_linux_web_app" "webappapi" {
    name = "api-${ var.project }-${ var.environment }"
    location = var.location
    resource_group_name = azurerm_resource_group.rg.name
    service_plan_id = azurerm_service_plan.sp.id

    site_config {
        always_on = true
        application_stack {
            docker_registry_url = "https://index.docker.io"
            docker_image_name = "nginx:latest"
        }
    }

    app_settings = {
        WEBSITES_PORT = "80"

        SQL_DRIVER = var.SQL_DRIVER
        SQL_SERVER = var.SQL_SERVER
        SQL_DATABASE = var.SQL_DATABASE
        SQL_USERNAME = var.SQL_USERNAME
        SQL_PASSWORD = var.admin_sql_password
        FIREBASE_API_KEY = var.FIREBASE_API_KEY
        SECRET_KEY = var.SECRET_KEY
        APPLICATIONINSIGHTS_CONNECTION_STRING = var.APPLICATIONINSIGHTS_CONNECTION_STRING
        REDIS_CONNECTION_STRING = var.REDIS_CONNECTION_STRING
    }

    tags = var.tags
}
