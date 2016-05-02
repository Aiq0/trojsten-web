# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.test import TestCase

from trojsten.contests.models import Competition, Series, Round
from trojsten.tasks.models import Task


class TaskListTests(TestCase):
    def setUp(self):
        competition = Competition.objects.create(name='TestCompetition')
        competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        series = Series.objects.create(number=1, name='Test series', competition=competition,
                                       year=1)
        self.round = Round.objects.create(number=1, series=series, visible=True,
                                          solutions_visible=True)
        self.url = reverse('task_list', kwargs={'round_id': self.round.id})

    def test_invalid_round(self):
        url = reverse('task_list', kwargs={'round_id': 47})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_no_tasks(self):
        response = self.client.get(self.url)
        # @ToDo: translations
        self.assertContains(response, 'Žiadne úlohy')

    def test_visible_tasks(self):
        Task.objects.create(number=1, name='Test task', round=self.round)
        response = self.client.get(self.url)
        # @ToDo: translations
        self.assertContains(response, 'Test task')


class TaskStatementsTests(TestCase):
    def setUp(self):
        competition = Competition.objects.create(name='TestCompetition')
        competition.sites.add(Site.objects.get(pk=settings.SITE_ID))
        series = Series.objects.create(number=1, name='Test series', competition=competition,
                                       year=1)
        self.round = Round.objects.create(number=1, series=series, visible=True,
                                          solutions_visible=True)
        self.task = Task.objects.create(number=1, name='Test task', round=self.round)
        self.url = reverse('task_statement', kwargs={'task_id': self.task.id})

    def test_invalid_task(self):
        url = reverse('task_statement', kwargs={'task_id': 47})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_task_statement(self):
        response = self.client.get(self.url)
        # @ToDo: translations
        self.assertContains(response, 'Test task')
