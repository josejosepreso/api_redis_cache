resource "azurerm_redis_cache" "cachedb" {
  name = "cache-${ var.project }-${ var.environment }"
  location = var.location
  resource_group_name  = azurerm_resource_group.rg.name
  capacity = 0
  family = "C"
  sku_name = "Basic"
  
  redis_configuration {
  }

  tags = var.tags
}
