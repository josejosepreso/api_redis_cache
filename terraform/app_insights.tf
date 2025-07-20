resource "azurerm_application_insights" "app_insights" {
  name = "ai-${ var.project }-${ var.environment }"
  location = var.location
  resource_group_name = azurerm_resource_group.rg.name
  application_type = "web"

  tags = var.tags
}
