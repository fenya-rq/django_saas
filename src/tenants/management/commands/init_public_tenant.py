from django.core.management.base import BaseCommand

from tenants.models import Domain, Tenant


class Command(BaseCommand):
    help = 'Initializes the public tenant and domain if they do not exist.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--domain',
            type=str,
            default='localhost',
            help='Domain name to associate with the public tenant (default: localhost).',
        )

    def handle(self, *args, **options):
        domain_name = options['domain']

        # Create or get the public tenant
        public_tenant, tenant_created = Tenant.objects.get_or_create(
            schema_name='public',
            defaults={'name': 'Public Tenant'},
        )

        if tenant_created:
            self.stdout.write(self.style.SUCCESS('✅ Public tenant created.'))
        else:
            self.stdout.write(self.style.WARNING('ℹ️ Public tenant already exists.'))

        # Create or get the domain for provided domain_name
        domain, domain_created = Domain.objects.get_or_create(
            domain=domain_name,
            tenant=public_tenant,
            defaults={'is_primary': True},
        )

        if domain_created:
            self.stdout.write(
                self.style.SUCCESS(f'✅ Domain "{domain_name}" linked to public tenant.')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'ℹ️ Domain "{domain_name}" already exists for public tenant.')
            )

        self.stdout.write(self.style.SUCCESS('Public tenant initialization complete.'))
