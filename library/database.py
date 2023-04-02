class DefaultDbRouter:
    _database = 'default'
    route_app_labels = {'admin', 'auth', 'contenttypes', 'sessions', 'messages'}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return self._database
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return self._database
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if (
                obj1._meta.app_label in self.route_app_labels or
                obj2._meta.app_label in self.route_app_labels
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels:
            return db == self._database
        return None


class ApiDbRouter:
    _database = 'api'
    route_app_labels = {_database}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return self._database
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return self._database
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if (
                obj1._meta.app_label in self.route_app_labels or
                obj2._meta.app_label in self.route_app_labels
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels:
            return db == self._database
        return None
