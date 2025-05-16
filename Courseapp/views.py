# Suggested code may be subject to a license. Learn more: ~LicenseLog:4254670771.
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from Users.models import Instructor

# Create your views here.
def index(request):
    return render(request,"base.html")


def course_list(request):
    courses = Course.objects.all()
    return render(request, 'course_list.html', {'courses': courses})

@user_passes_test(lambda u: Instructor.objects.filter(profile=u.profile).exists())
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('course_list')
    else:
        form = CourseForm()
    return render(request, 'course_form.html', {'form': form})

@user_passes_test(lambda u: Instructor.objects.filter(profile=u.profile).exists())
def course_update(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            return redirect('course_list')
    else:
        form = CourseForm(instance=course)
    return render(request, 'course_form.html', {'form': form})

@user_passes_test(lambda u: Instructor.objects.filter(profile=u.profile).exists())
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':# Suggested code may be subject to a license. Learn more: ~LicenseLog:3694217246.
        course.delete()
        return redirect('course_list')
    return render(request, 'course_confirm_delete.html', {'course': course})

def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    return render(request, 'course_detail.html', {'course': course})

