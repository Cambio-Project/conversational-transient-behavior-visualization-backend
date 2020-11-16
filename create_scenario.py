from chatbot_webservice.models import Service, Dependency

old_scenario = 0
new_scenario = 2
service_names = ['Frontend', 'User', 'Catalogue', 'Cart', 'Order', 'Payment', 'Shipping']

# Create services
for name in service_names:
    service = Service.objects.get(system='SockShop', scenario=old_scenario, name=name)

    Service.objects.create(
        scenario=new_scenario,
        system='SockShop',
        name=name,
        endpoints=service.endpoints
    )
    print(f'Created {name} service')

# Create dependencies
old_deps = Dependency.objects.filter(system='SockShop', scenario=old_scenario)
for dep in old_deps:
    source_name = dep.source.name
    target_name = dep.target.name
    source = Service.objects.get(system='SockShop', scenario=new_scenario, name=source_name)
    target = Service.objects.get(system='SockShop', scenario=new_scenario, name=target_name)

    Dependency.objects.create(
        system='SockShop',
        scenario=new_scenario,
        source=source,
        target=target
    )
    print(f'Created dependency between {source_name} and {target_name}')

