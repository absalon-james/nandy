"""Module with classes for manipulating usage data."""


class UsageReport(object):
    """Class that manipulates nova.usage.list() data."""

    def __init__(self, usage_list):
        """Init the report object.

        :param usage_list: List created by nova.usage.list()
        """
        # Store tenant data by tenant to aid in retrieval
        self.tenant_data = {}
        for tenant_data in usage_list:
            self.tenant_data[tenant_data.tenant_id] = tenant_data

    def super_stat(self, stat, tenant_id=None):
        """Get tenant wide stat.

        :param stat: String name of stat to get
        :param tenant_id: If provided isolate to one tenant
        :returns: Numeric sum of stat
        """
        if tenant_id is not None:
            tenants = [self.tenant_data[tenant_id]]
        else:
            tenants = self.tenant_data.values()
        getstat = lambda t: getattr(t, stat)
        return sum(map(getstat, tenants))

    def active_server_stat(self, stat, tenant_id=None):
        """Get tenant active stat.

        :param stat: String name of stat
        :param tenant_id: String name of tenant.
        :returns: Sum of stat on active instances.
        """
        if tenant_id is not None:
            tenants = [self.tenant_data[tenant_id]]
        else:
            tenants = self.tenant_data.values()
        activestat = lambda s: s[stat] if s.get('state') == 'active' else 0
        tenantstat = lambda t: sum(map(activestat, t.server_usages))
        return sum(map(tenantstat, tenants))

    def total_vcpu_usage(self, tenant_id=None):
        """Get total vcpus usage in vcpu hours.

        :param tenant_id: String id of tenant
        :return Float:
        """
        return self.super_stat('total_vcpus_usage', tenant_id=tenant_id)

    def total_local_gb_usage(self, tenant_id=None):
        """Get total storage usage in GB hours.

        :param tenant_id: String id of tenant
        :returns: float
        """
        return self.super_stat('total_local_gb_usage', tenant_id=tenant_id)

    def total_memory_mb_usage(self, tenant_id=None):
        """Get total memory usage in MB hours.

        :param tenant_id: String id of tenant
        :returns: float
        """
        return self.super_stat('total_memory_mb_usage', tenant_id=tenant_id)

    def active_vcpus(self, tenant_id=None):
        """Get active vcpus.

        :param tenant_id: String id of the tenant
        :returns: Integer
        """
        return self.active_server_stat('vcpus', tenant_id=tenant_id)

    def active_local_storage_gb(self, tenant_id=None):
        """Get active local storage GB.

        :param tenant_id: String id of the tenant
        :returns: Float
        """
        return self.active_server_stat('local_gb', tenant_id=tenant_id)

    def active_memory_mb(self, tenant_id=None):
        """Get active memory in MB.

        :param tenant_id: String id of tenant
        :returns: Float
        """
        return self.active_server_stat('memory_mb', tenant_id=tenant_id)

    def active_stats(self, tenant_id=None):
        """Get three tuple of active vcpus, memory, and storage.

        :param tenant_id: String id of tenant.
        :return: tuple
        """
        vcpus = self.active_vcpus(tenant_id=tenant_id)
        memory = self.active_memory_mb(tenant_id=tenant_id)
        storage = self.active_local_storage_gb(tenant_id=tenant_id)
        return (vcpus, memory, storage)
