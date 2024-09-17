from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from django.db.models import Count
from .models import Quiz, Question, Answer
from django.core.paginator import Paginator
from typing import Optional
import random


def start_quiz_view(request) -> HttpResponse:
    topics = Quiz.objects.all().annotate(questions_count=Count('question'))
    return render(request, 'start.html', context={'topics': topics})


def get_questions(request, is_start=False) -> HttpResponse:
    if is_start:
        request = _reset_quiz(request)
        question = _get_first_question(request)
        question_number = 1
    else:
        question = _get_subsequent_question(request)
        if question is None:
            return get_finish(request)
        question_number = request.session.get('question_number', 1) + 1

    answers = Answer.objects.filter(question=question)
    request.session['question_id'] = question.id  # Update session state with current question id.
    request.session['question_number'] = question_number  # Update session state with current question number.

    return render(request, 'partials/question.html', context={
        'question': question,
        'answers': answers,
        'question_number': question_number
    })


def _get_first_question(request) -> Question:
    quiz_id = request.POST['quiz_id']
    
    # Get all question IDs for the selected quiz and shuffle them
    question_ids = list(Question.objects.filter(quiz_id=quiz_id).values_list('id', flat=True))
    random.shuffle(question_ids)
    
    # Store the shuffled question IDs in the session
    request.session['shuffled_questions'] = question_ids
    
    # Return the first question in the shuffled list
    first_question_id = question_ids[0]
    return Question.objects.get(id=first_question_id)


def _get_subsequent_question(request) -> Optional[Question]:
    shuffled_questions = request.session.get('shuffled_questions', [])
    previous_question_id = request.session['question_id']

    # Find the index of the previous question and get the next one
    try:
        current_index = shuffled_questions.index(previous_question_id)
        next_question_id = shuffled_questions[current_index + 1]
        return Question.objects.get(id=next_question_id)
    except (IndexError, ValueError, Question.DoesNotExist):
        # If no more questions are available or some error occurs
        return None


def get_answer(request) -> HttpResponse:
    submitted_answer_id = request.POST['answer_id']
    submitted_answer = Answer.objects.get(id=submitted_answer_id)

    if submitted_answer.is_correct:
        correct_answer = submitted_answer
        request.session['score'] = request.session.get('score', 0) + 1
    else:
        correct_answer = Answer.objects.get(
            question_id=submitted_answer.question_id, is_correct=True
        )

    return render(
        request, 'partials/answer.html', context={
            'submitted_answer': submitted_answer,
            'answer': correct_answer,
        }
    )


def get_finish(request) -> HttpResponse:
    quiz = Question.objects.get(id=request.session['question_id']).quiz
    questions_count = len(request.session.get('shuffled_questions', []))
    score = request.session.get('score', 0)
    percent = int(score / questions_count * 100)
    request = _reset_quiz(request)

    return render(request, 'partials/finish.html', context={
        'questions_count': questions_count, 'score': score, 'percent_score': percent
    })


def _reset_quiz(request) -> HttpRequest:
    """
    We reset the quiz state to allow the user to start another quiz.
    """
    if 'question_id' in request.session:
        del request.session['question_id']
    if 'score' in request.session:
        del request.session['score']
    if 'shuffled_questions' in request.session:
        del request.session['shuffled_questions']
    return request





# from django.shortcuts import render
# from django.http import HttpResponse, HttpRequest
# from django.db.models import Count
# from .models import Quiz, Question, Answer
# from django.core.paginator import Paginator
# from typing import Optional


# def start_quiz_view(request) -> HttpResponse:
#   topics = Quiz.objects.all().annotate(questions_count=Count('question'))
#   return render(
#     request, 'start.html', context={'topics': topics}
#   )


# def get_questions(request, is_start=False) -> HttpResponse:
#     if is_start:
#         request = _reset_quiz(request)
#         question = _get_first_question(request)
#         question_number = 1
#     else:
#         question = _get_subsequent_question(request)
#         if question is None:
#             return get_finish(request)
#         question_number = request.session.get('question_number', 1) + 1

#     answers = Answer.objects.filter(question=question)
#     request.session['question_id'] = question.id  # Update session state with current question id.
#     request.session['question_number'] = question_number  # Update session state with current question number.

#     return render(request, 'partials/question.html', context={
#         'question': question,
#         'answers': answers,
#         'question_number': question_number
#     })


# # def get_questions(request, is_start=False) -> HttpResponse:
# #   if is_start:
# #     request = _reset_quiz(request)
# #     question = _get_first_question(request)
# #   else:
# #     question = _get_subsequent_question(request)
# #     if question is None:
# #       return get_finish(request)

# #   answers = Answer.objects.filter(question=question)
# #   request.session['question_id'] = question.id  # Update session state with current question id.

# #   return render(request, 'partials/question.html', context={
# #     'question': question, 'answers': answers
# #   })


# def _get_first_question(request) -> Question:
#   quiz_id = request.POST['quiz_id']
#   return Question.objects.filter(quiz_id=quiz_id).order_by('id').first()


# def _get_subsequent_question(request) -> Optional[Question]:
#   quiz_id = request.POST['quiz_id']
#   previous_question_id = request.session['question_id']

#   try:
#     return Question.objects.filter(
#       quiz_id=quiz_id, id__gt=previous_question_id
#     ).order_by('id').first()
#   except Question.DoesNotExist:  # I.e., there are no more questions.
#     return None


# def get_answer(request) -> HttpResponse:
#   submitted_answer_id = request.POST['answer_id']
#   submitted_answer = Answer.objects.get(id=submitted_answer_id)

#   if submitted_answer.is_correct:
#     correct_answer = submitted_answer
#     request.session['score'] = request.session.get('score', 0) + 1
#   else:
#     correct_answer = Answer.objects.get(
#       question_id=submitted_answer.question_id, is_correct=True
#     )

#   return render(
#     request, 'partials/answer.html', context={
#       'submitted_answer': submitted_answer,
#       'answer': correct_answer,
#     }
#   )


# def get_finish(request) -> HttpResponse:
#   quiz = Question.objects.get(id=request.session['question_id']).quiz
#   questions_count = Question.objects.filter(quiz=quiz).count()
#   score = request.session.get('score', 0)
#   percent = int(score / questions_count * 100)
#   request = _reset_quiz(request)

#   return render(request, 'partials/finish.html', context={
#     'questions_count': questions_count, 'score': score, 'percent_score': percent
#   })


# def _reset_quiz(request) -> HttpRequest:
#   """
#   We reset the quiz state to allow the user to start another quiz.
#   """
#   if 'question_id' in request.session:
#     del request.session['question_id']
#   if 'score' in request.session:
#     del request.session['score']
#   return request



