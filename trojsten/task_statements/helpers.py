from trojsten.regal.contests.models import Round
from trojsten.regal.tasks.models import Submit
from django.db.models import F


def get_rounds_by_year(user, competition):
    rounds = Round.visible_rounds(
        user
    ).filter(
        series__competition=competition
    ).order_by(
        '-series__year', '-number'
    ).select_related('series__year')
    rounds_dict = dict()
    for round in rounds:
        if not round.series.year in rounds_dict:
            rounds_dict[round.series.year] = list()
        rounds_dict[round.series.year].append(round)
    return rounds_dict


def get_result_rounds(round):
    rounds = Round.objects.filter(
        visible=True, series=round.series, number__lte=round.number
    ).order_by('number')
    return ','.join(str(r.id) for r in rounds)


def get_latest_submits_for_user(tasks, user):
    '''Returns latest submits which belong to specified tasks and user.
    Only one submit per submit type and task is returned.
    '''
    return Submit.objects.filter(
        user=user,
        task__in=tasks,
        time__lte=F('task__round__end_time'),
    ).order_by(
        'task', 'submit_type', '-time', '-id',
    ).distinct(
        'task', 'submit_type'
    )


def get_points_from_submits(tasks, submits):
    '''Returns results data for each task
    '''
    res = {i: {'description': 0, 'source': 0} for i in tasks}
    for submit in submits:
        if submit.submit_type == Submit.DESCRIPTION:
            res[submit.task]['description'] = '??'  # Fixme
        else:
            res[submit.task]['source'] += submit.user_points
    return res
