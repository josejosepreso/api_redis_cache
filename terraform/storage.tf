resource "azurerm_storage_account" "saccount" {
    name = "sa${ lower(var.project) }${ var.environment }"
    resource_group_name = azurerm_resource_group.rg.name
    location = var.location
    account_tier = "Standard"
    account_replication_type = "LRS"

    tags = var.tags
}

resource "azurerm_storage_container" "c1" {
    name = "source"
    container_access_type = "private"
    storage_account_id = azurerm_storage_account.saccount.id
}
