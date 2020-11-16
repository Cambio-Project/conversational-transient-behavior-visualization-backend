from chatbot_webservice.models import Service, Dependency

system = 'SockShop'

# Delete old dependencies
Dependency.objects.filter(system=system).delete()

# Create new dependencies
service_names = ['User', 'Catalogue', 'Cart', 'Order', 'Payment']

for scenario in range(0, 3):
    frontend = Service.objects.get(system=system, scenario=scenario, name='Frontend')
    for name in service_names:
        source = Service.objects.get(system=system, scenario=scenario, name=name)

        Dependency.objects.create(
            system=system,
            scenario=scenario,
            source=source,
            target=frontend
        )

    order = Service.objects.get(system=system, scenario=scenario, name='Order')
    shipping = Service.objects.get(system=system, scenario=scenario, name='Shipping')

    Dependency.objects.create(
        system=system,
        scenario=scenario,
        source=shipping,
        target=order
    )
