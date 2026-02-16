 @classmethod
    def _slug(cls, value: models.BaseModel | tuple[int, str]) -> str:
        website = getattr(request, 'website', None)

        # Special case for product.template
        if getattr(value, '_name', None) == 'product.template':
            try:
                identifier, name, ref = value.id, value.name, value.default_code
            except AttributeError:
                # assume name_search result tuple
                identifier, name = value
                ref = ''

            if not identifier:
                raise ValueError("Cannot slug non-existent record %s" % value)

            slugname = cls._slugify(name or '')
            if not slugname:
                slugname = str(identifier)

            if website and website.is_app_tegel_be:
               return f"art/{ref}" if ref else slugname

            return f"product/{slugname}/{ref}" if ref else slugname

        # Default behavior for other models
        return super()._slug(value)
