
from django.db import models
from django.test import TestCase,TransactionTestCase
from utils import *

class NormalizeTest(TestCase):
    def test_normalize(self):
        """
        tests to normalize the query
        """
        self.assertEquals(
            normalize_query('  some random  words "with   quotes  " and   spaces'),
            ['some', 'random', 'words', 'with quotes', 'and', 'spaces']
        )

        self.assertEquals(
            normalize_query('  adsf add a & and a | "for good%measure"'),
            ['adsf','add','a','&','and','a','|',"for good%measure"]
        )

    def test_empty_string(self, ):
        """
        """
        self.assertEquals(normalize_query(""),[])

class BuildQueryTest(TestCase):

    def test_find_items_in_database(self, ):
        """
        test to find the items based on fields
        """

        query = build_query("now is the time",['name','description'])

        self.assertEquals(len(query),4)

        self.assertEquals(
            str(query),
            "(AND: (OR: ('name__icontains', 'now'), ('description__icontains', 'now')), (OR: ('name__icontains', 'is'), ('description__icontains', 'is')), (OR: ('name__icontains', 'the'), ('description__icontains', 'the')), (OR: ('name__icontains', 'time'), ('description__icontains', 'time')))"
        )

    def test_return_none_for_empty_string(self):
        """
        If string withouth terms is provided to build_query then return None

        """
        query = build_query(' ', ['name', 'description'])

        self.assertIsNone(query)


class SearchTest(TransactionTestCase):
    """
    """

    def setUp(self, ):

        self.entry=Entry.objects.get_or_create(name="Now", description="is the time")[0]

        Entry.objects.get_or_create(name="Item 2",description="do we have time?")

        self.freds = [
            Entry.objects.get_or_create(name="Is",description="fred flintstone")[0],
            Entry.objects.get_or_create(name="barney rubble",description="fred's neighbor")[0],
            ]


    def test_generic_query(self, ):
        """
        """

        request = MockRequest({"q":"now is the time"})

        result = generic_search(request,Entry,["name","description"])

        self.assertEquals(list(result),
                    [self.entry,]
        )

    def test_generic_empty_query_returns_all(self,):
        """
        """
        request = MockRequest({})
        result = generic_search(request, Entry, ["name","description"])

        self.assertEquals(set(result),
                          set(Entry.objects.all())
        )
        
    def test_multiple_records(self, ):
        """
        """
        result = perform_search("fred", Entry, ["name","description"])

        self.assertEquals(list(result),
                    self.freds
        )

    def test_queryset(self,):
        result = perform_search(
            "time", Entry.objects.filter(name="Now"), ['description'],
        )
        self.assertEquals(list(result),
                    [self.entry,]
        )


class MockRequest(object):

    def __init__(self, get_params):
        """
        """
        self.GET=get_params


class Entry(models.Model):

    name=models.CharField(max_length=50)
    description=models.TextField()

    def __unicode__(self, ):
        """
        """
        return self.name

