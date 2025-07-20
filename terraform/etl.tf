resource "azurerm_data_factory" "etl_orchestrator" {
    name = "df-${lower(var.project)}-${lower(var.environment)}"
    location = var.location
    resource_group_name = azurerm_resource_group.rg.name
    tags = var.tags
}
