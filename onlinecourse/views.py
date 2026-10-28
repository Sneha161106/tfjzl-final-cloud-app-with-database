from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Course, Lesson, Enrollment, Question, Choice, Submission

# Existing views (index, course_details, etc.) remain here...

def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    
    # Get user enrollment for this course
    enrollment = Enrollment.objects.get(user=user, course=course)
    
    if request.method == 'POST':
        # Create a new submission instance
        submission = Submission.objects.create(enrollment=enrollment)
        
        # Collect selected choices from POST request
        selected_ids = []
        for key, value in request.POST.items():
            if key.startswith('choice_'):
                selected_ids.append(int(value))
        
        # Add selected choices to submission
        choices = Choice.objects.filter(id__in=selected_ids)
        submission.choices.set(choices)
        submission.save()
        
        return HttpResponseRedirect(reverse('onlinecourse:show_exam_result', args=(course.id, submission.id)))

def show_exam_result(request, course_id, submission_id):
    context = {}
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    
    # Extract selected choice IDs
    selected_ids = [choice.id for choice in submission.choices.all()]
    
    total_score = 0
    grade = 0
    
    # Calculate score based on correct choices
    for question in course.question_set.all():
        total_score += question.grade
        if question.is_get_score(selected_ids):
            grade += question.grade
            
    context['course'] = course
    context['grade'] = grade
    context['total_score'] = total_score
    context['submission'] = submission
    context['selected_ids'] = selected_ids
    
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)