from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.db.models import Case, When, Value, IntegerField
from django.utils import timezone
import time
from experiences.models import Group, Person, Participation

class Command(BaseCommand):
    help = 'Pre-warms the cache for improved admin performance'

    def add_arguments(self, parser):
        parser.add_argument(
            '--groups',
            action='store_true',
            dest='groups_only',
            help='Only pre-warm group-related caches',
        )
        parser.add_argument(
            '--persons',
            action='store_true',
            dest='persons_only',
            help='Only pre-warm person-related caches',
        )
        parser.add_argument(
            '--years',
            action='store_true',
            dest='years_only',
            help='Only pre-warm year selector caches',
        )

    def handle(self, *args, **options):
        start_time = time.time()
        total_cached = 0
        
        do_all = not any([options['groups_only'], options['persons_only'], options['years_only']])
        
        # Cache year choices for YearSelectorWidget
        if do_all or options['years_only']:
            self.stdout.write("Pre-warming year choices cache...")
            
            current_year = timezone.now().year
            year_range = 5  # Match the default in YearSelectorWidget
            years = list(range(current_year - year_range, current_year + 1))
            
            year_choices = []
            for year in sorted(years, reverse=True):
                school_year = f"{year}-{year+1}"
                year_choices.append({
                    'year': year,
                    'school_year': school_year,
                })
            
            cache_key = 'year_selector_choices'
            cache.set(cache_key, year_choices, 60 * 60 * 24 * 30)  # Cache for 30 days
            total_cached += 1
            self.stdout.write(self.style.SUCCESS(f"Cached year choices for selector widget"))
            
        # Cache Person participation querysets
        if do_all or options['persons_only']:
            self.stdout.write("Pre-warming person participation caches...")
            persons = Person.objects.all()
            count = 0
            
            for person in persons:
                cache_key = f'participation_inline_person_{person.pk}'
                
                # Get participations with annotations
                queryset = Participation.objects.filter(person=person).annotate(
                    sort_order=Case(
                        When(person__role__title='Facilitator', then=Value(1)),
                        default=Value(2),
                        output_field=IntegerField(),
                    )
                ).order_by('sort_order', 'person__user__first_name', 'person__user__last_name')
                
                cache.set(cache_key, queryset, 60 * 60 * 24 * 7)  # Cache for a week
                count += 1
                
                # Give feedback every 50 items
                if count % 50 == 0:
                    self.stdout.write(f"  - Cached {count}/{persons.count()} person participation lists...")
            
            total_cached += count
            self.stdout.write(self.style.SUCCESS(f"Cached {count} person participation querysets"))
        
        # Cache Group participation querysets
        if do_all or options['groups_only']:
            self.stdout.write("Pre-warming group participation caches...")
            groups = Group.objects.all()
            count = 0
            
            for group in groups:
                cache_key = f'participation_inline_group_{group.pk}'
                
                # Get participations with annotations
                queryset = Participation.objects.filter(group=group).annotate(
                    sort_order=Case(
                        When(person__role__title='Facilitator', then=Value(1)),
                        default=Value(2),
                        output_field=IntegerField(),
                    )
                ).order_by('sort_order', 'person__user__first_name', 'person__user__last_name')
                
                cache.set(cache_key, queryset, 60 * 60 * 24 * 7)  # Cache for a week
                count += 1
                
                # Give feedback every 20 items
                if count % 20 == 0:
                    self.stdout.write(f"  - Cached {count}/{groups.count()} group participation lists...")
            
            total_cached += count
            self.stdout.write(self.style.SUCCESS(f"Cached {count} group participation querysets"))
        
        elapsed_time = time.time() - start_time
        self.stdout.write(
            self.style.SUCCESS(f"Successfully pre-warmed {total_cached} cache items in {elapsed_time:.2f} seconds")
        )
