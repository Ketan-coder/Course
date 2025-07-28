import email
import uuid
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
# Create your views here.
from django.contrib.auth.views import (PasswordResetCompleteView,
                                       PasswordResetConfirmView,
                                       PasswordResetDoneView,
                                       PasswordResetView)
from django.core.mail import EmailMultiAlternatives
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView
# from Notes.models import Activity
from utils.utils import send_email_using_resend
from utils.models import Activity, Currency, PhoneNoPrefix

from Course import settings as project_settings
from utils.media_handler import MediaHandler
from .forms import ProfileForm, UserRegistrationForm
from .models import Profile, Instructor, Student

#  Request Password Reset (User submits email)
class CustomPasswordResetView(PasswordResetView):
    template_name = "user/password_reset.html"
    email_template_name = "user/password_reset_email.html"
    subject_template_name = "user/password_reset_subject.txt"
    success_url = reverse_lazy("password_reset_done")


#  Password Reset Done (Email sent confirmation page)
class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = "user/password_reset_done.html"


#  Password Reset Confirm (User sets new password)
class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "user/password_reset_confirm.html"
    success_url = reverse_lazy("password_reset_complete")


#  Password Reset Complete (Password successfully changed)
class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "user/password_reset_complete.html"


@login_required
def updateUser(request):
    user = request.user
    request.session['page'] = 'update_user'
    # Ensure email is verified before allowing profile update
    if not user.is_active:
        messages.error(
            request, "You must verify your email before updating your profile."
        )
        return redirect("email_confirmation_pending")

    profile = Profile.objects.get(user=user)
    currencies = Currency.objects.all()
    phone_no_prefixes = PhoneNoPrefix.objects.all().order_by('-created_at')
    if Student.objects.filter(profile=profile).exists():
        is_student = True
    elif Instructor.objects.filter(profile=profile).exists():
        is_student = False
        instructor = Instructor.objects.get(profile=profile)

    if request.method == "POST":
        username: str = request.POST.get("username", "").strip() or user.username
        email: str = request.POST.get("email", "").strip() or user.email
        first_name: str = request.POST.get("first_name", "").strip()
        last_name: str = request.POST.get("last_name", "").strip()
        bio: str = request.POST.get("bio", "").strip()

        # Check if username exists in User or Profile (excluding the current user)
        if username and (
            User.objects.filter(username=username).exclude(pk=user.pk).exists()
        ):
            messages.error(request, "❌ Username is already taken.")
            return redirect("update_user")

        # Check if email exists in User or Profile (excluding the current user)
        if email and (
            User.objects.filter(email=email).exclude(pk=user.pk).exists()
        ):
            messages.error(request, "❌ Email is already in use.")
            return redirect("update_user")

        #  Save Updates
        user.username = username
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        profile.bio = bio
        profile.phone_no = request.POST.get("phone_no", "").strip() or profile.phone_no
        profile.phone_no_prefix_id = request.POST.get(
            "phone_no_prefix", ""
        ).strip() or profile.phone_no_prefix
        profile.address = request.POST.get("address", "").strip() or profile.address
        # profile.date_of_birth = request.POST.get("date_of_birth", profile.date_of_birth).strip()
        date_of_birth_str = request.POST.get('date_of_birth')
        if date_of_birth_str:
            try:
                profile.date_of_birth = datetime.strptime(date_of_birth_str, "%Y-%m-%d").date()
            except ValueError:
                profile.date_of_birth = None
        else:
            profile.date_of_birth = None
        profile.image = request.FILES.get("profile_pic", profile.image)
        if request.POST.get("currencies"):
            currency = get_object_or_404(Currency, pk=request.POST.get("currencies"))
            profile.currency = currency or profile.currency
        profile.is_profile_complete = all([profile.phone_no,profile.phone_no_prefix, profile.address, profile.date_of_birth, profile.image, profile.currency])
        profile.is_email_verified = (
            bool(profile.user.email and user.is_active and profile.email_confirmation_token is None)
        )
        profile.is_phone_verified = bool(profile.phone_no and user.is_active)
        profile.save()

        if not is_student:
            instructor = Instructor.objects.get(profile=profile)
            instructor.experience = request.POST.get("experience", instructor.experience).strip()
            instructor.save()

        if project_settings.DEBUG is False:
            try:
                send_email_using_resend(
                    to_email=user.email,
                    subject="Profile Update Alert",
                    title="Profile Update Alert Notification",
                    body=f"Your profile with username '{user.username}' was updated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}. If this was not you, please log in to secure your account!.",
                    anchor_link=f"https://{settings.SITE_URL}/accounts/password-reset/",
                    anchor_text="Reset Password",
                )
            except Exception as error:
                messages.error(request, f"Error sending email: {error}")
                return redirect("update_user")
        
        Activity.objects.create(
            user=user,
            activity_type="Profile Update",
            description=f"Updated profile for {user.username}",
        )

        messages.success(request, "Profile updated successfully")
        return redirect("home")

    context = {"user": user, "profile": profile, "is_student": is_student, "instructor": instructor if not is_student else None, 
               "currencies": currencies, "phone_no_prefixes": phone_no_prefixes, "title": "Update User Profile"}
    return render(request, "user/userupdate.html", context)


def login_form(request):
    context = {"title": "Login"}
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            if project_settings.DEBUG is False:
                try:
                    print("user.email", user.email)
                    send_email_using_resend(
                        to_email=user.email,
                        subject="Login Alert",
                        title="Login Alert Notification",
                        body=f"Your account with username '{user.username}' was accessed on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}. If this was not you, please reset your password to secure your account!.",
                        anchor_link=f"https://{settings.SITE_URL}/accounts/password-reset/",
                        anchor_text="Reset Password",
                    )
                except Exception as error:
                    messages.error(request, f"Error sending email: {error}")
                    return redirect("login")
            # subject, from_email, to = (
            #     "Login Alert",
            #     "sajan@gmail.com",
            #     f"{user.email}",
            # )
            # text_content = "This is an important message."
            # html_content = f'<html lang="en" xmlns="http://www.w3.org/1999/xhtml" xmlns:o="urn:schemas-microsoft-com:office:office">\n<head><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200&display=swap" rel="stylesheet">\n<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="x-apple-disable-message-reformatting"><title></title></head<body style="margin:0;padding:0;font-family:"Poppins",Arial,sans-serif;"><table role="presentation" style="width:100%;border-collapse:collapse;border:0;border-spacing:0;background:#ffffff;"><tr><td align="center" style="padding:0;"><table role="presentation" style="width:602px;border-collapse:collapse;border:1px solid #cccccc;border-spacing:0;text-align:left;"><tr><td align="center" style="padding:40px 0 30px 0;background:#efefef;"><h1>sajan</h1></td></tr><tr><td style="padding:36px 30px 42px 30px;"><table role="presentation" style="width:100%;border-collapse:collapse;border:0;border-spacing:0;"><tr><td style="padding:0 0 36px 0;color:#153643;"><h1 style="font-size:24px;margin:0 0 20px 0;font-family:Arial,sans-serif;">Login Alert Mail</h1><p style="margin:0 0 12px 0;font-size:16px;line-height:24px;font-family:Arial,sans-serif;">This is to tell you that your account with username: {username} signing in at {datetime.now()}, If this is not you please consider changing your password immediately!</p><h3 style="margin:0;line-height:24px;font-family:Arial,sans-serif;"><a href="https://codingfox.pythonanywhere.com/users/password-reset/" style="padding: 1%; background-color: #0076d1; color: white;text-decoration: none;">Reset Password!</a></h3><br><p>Please do not reply to this email address, Mail me here: <a href="mailto:ketanv288@gmail.com" style="background-color: transparent; color: #0076d1;text-decoration: none;">Mail Me!</a></p></td></tr></table></body></html>'
            # msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            # msg.attach_alternative(html_content, "text/html")
            # msg.send()
            
            try:
                profile = Profile.objects.get(user=user)
                if Instructor.objects.filter(profile=profile).exists():
                    messages.success(request, "Welcome Back Instructor!")
                    Activity.objects.create(
                        user=user,
                        activity_type="Login",
                        description=f"Logged in as Instructor: {user.username}",
                    )
                elif Student.objects.filter(profile=profile).exists():
                    messages.success(request, f"Welcome Back {user.first_name}! Start Learning by doing")
                    Activity.objects.create(
                        user=user,
                        activity_type="Login",
                        description=f"Logged in as Student: {user.username}",
                    )
                return redirect("home")
            except Profile.DoesNotExist:
                messages.error(request, "Profile isn't created for this user.")
            except Exception as error:
                messages.error(request, f"Unexpected error: {error}")
            return redirect("login")
        else:
            messages.error(request, f"Account Does Not Exists with {username}")
            return render(request, "user/login.html", context)
    return render(request, "user/login.html", context)


def logout_form(request):
    context = {"title": "Logout"}
    logout(request)
    # return render(request, "user/logout.html", context)
    return redirect("home")

def registeration_form(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            email = form.cleaned_data.get("email")
            messages.success(request, f"Account created for {username}! Just Login")
            # messages.warning(request,f'Upon Regiestering you are agreeing with the using required cookies')
            # subject, from_email, to = f'Welcome {username}', 'codingfoxblogs@gmail.com', f'{email}'
            # text_content = 'This is an important message.'
            # html_content = (f'<div style="background-color: hsl(206, 98%, 90%);color: #363636;width: 90%;height: auto;font-weight: 300;padding: 5%;"><h1 style="text-align:center;">Welcome {username}!</h1><br><h3> Explore the website CodingFox Blogs, you can also create Blogs on this blog page at no cost<br><a href="https://codingfox.pythonanywhere.com/" style="padding: 1%; background-color: #0076d1; color: white;text-decoration: none;">Explore More!</a></h3><br><p>Please do not reply to this gmail, if you want to contact mail here for any query <a href="mailto:ketanv288@gmail.com">📧Mail Me</a></p></div>')
            # msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            # msg.attach_alternative(html_content, "text/html")
            # msg.send()
            return redirect("login")
    else:
        form = UserRegistrationForm()
    context = {"title": "Register", "form": form}
    return render(request, "user/newuser.html", context)


def register_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password1")
        confirm_password = request.POST.get("password2")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "user/register.html", {"title": "Register"})

        existing_user = User.objects.filter(email=email).first()
        if existing_user:
            messages.error(request, "Email is already registered. Try logging in.")
            return render(request, "user/register.html", {"title": "Register"})

        #  Step 1: Create User First
        user = User.objects.create_user(username=email, email=email, password=password)
        user.is_active = False  # User is inactive until email confirmation
        user.save()

        profile = Profile.objects.get(user=user)
        profile.email_confirmation_token = uuid.uuid4()
        profile.save()

        #  Step 4: Send Confirmation Email
        confirmation_link = f"{settings.SITE_URL}/accounts/confirm-email/{profile.email_confirmation_token}/"
        if project_settings.DEBUG is False:
            try:
                send_email_using_resend(
                    to_email=user.email,
                    subject="Confirm Your sajan Account",
                    title="Complete Your Registration",
                    body="Thank you for registering! Please confirm your email by clicking the button below.",
                    anchor_link=confirmation_link,
                    anchor_text="Confirm Email",
                )
            except Exception as error:
                messages.error(request, f"Error sending confirmation email: {error}")
                return render(request, "user/register.html", {"title": "Register"})
        print(confirmation_link)
        # subject = "Confirm Your sajan Account"
        # from_email = "codingfoxblogs@gmail.com"
        # to = user.email
        # text_content = "Please confirm your email."
        # html_content = f'''
        # <html lang="en">
        # <head>
        #     <meta charset="UTF-8">
        #     <meta name="viewport" content="width=device-width, initial-scale=1">
        #     <title>Email Confirmation</title>
        # </head>
        # <body style="font-family: 'Poppins', Arial, sans-serif; background: #ffffff; padding: 20px;">
        #     <h2 style="color: #0076d1;">Confirm Your Email for sajan</h2>
        #     <p>Hello,</p>
        #     <p>Thank you for registering with sajan. Please click the link below to confirm your email address:</p>
        #     <p><a href="{confirmation_link}" style="padding: 10px; background-color: #0076d1; color: white; text-decoration: none;">Confirm Email</a></p>
        #     <p>If you did not sign up, please ignore this email.</p>
        # </body>
        # </html>
        # '''
        # msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        # msg.attach_alternative(html_content, "text/html")
        # msg.send()

        Activity.objects.create(
            user=user,
            activity_type="Registration",
            description=f"Registered user: {user.username}",
        )

        messages.success(
            request,
            "Registration successful. Check your email to confirm your account.",
        )
        return redirect("email_confirmation_pending")  #  Fixed the URL name

    return render(request, "user/register.html", {"title": "Register"})


def email_confirmation_view(request, token):

    try:
        token_uuid = uuid.UUID(token)  #  Convert token from str to UUID
    except ValueError:
        raise Http404("Invalid Token Format")  # If the token is not a valid UUID

    try:
        profile = Profile.objects.get(
            email_confirmation_token=token_uuid
        )  #  Query with UUID
    except Profile.DoesNotExist:
        raise Http404("Invalid or Expired Token")

    # Activate user and remove token
    profile.user.is_active = True
    profile.user.save()
    profile.email_confirmation_token = None  # Remove token after activation
    profile.is_email_verified = True
    profile.save()

    # Student.objects.create(profile=profile)

    login(request, profile.user)
    messages.success(request, "Email confirmed! Complete your profile.")
    return redirect("profile_setup")

@login_required
def profile_setup_view(request):
    if not request.user.is_authenticated:
        return redirect("login")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        bio = request.POST.get("bio", "").strip()
        phone_no_prefix = request.POST.get("phone_no_prefix", "").strip()
        phone_no = request.POST.get("phone_no", "").strip()
        address = request.POST.get("address", "").strip()
        date_of_birth_raw = request.POST.get("date_of_birth", "").strip()
        profile_pic = request.FILES.get("profile_pic")

        # Validate required fields
        if not username:
            messages.error(request, "Username cannot be empty.")
        elif User.objects.filter(username=username).exclude(id=request.user.id).exists():
            messages.error(request, "Username is already taken.")
        elif not phone_no.isdigit():
            messages.error(request, "Phone number must contain only digits.")
        elif not phone_no_prefix.isdigit():
            messages.error(request, "Phone number prefix must contain only digits.")
        elif date_of_birth_raw:
            try:
                date_of_birth = datetime.strptime(date_of_birth_raw, "%Y-%m-%d").date()
            except ValueError:
                messages.error(request, "Invalid date format. Use YYYY-MM-DD.")
                return render(request, "user/profile_setup.html", {"title": "Complete Profile"})
        else:
            date_of_birth = None

        # Validate image file if uploaded
        profile_pic_path = None
        if profile_pic_file and MediaHandler.is_image(profile_pic_file.name):
            resized_path = MediaHandler.resize_image(profile_pic_file)
            if resized_path:
                profile_pic_path = resized_path
            else:
                messages.error(request, "Failed to process the image.")
                return render(request, "user/profile_setup.html", {"title": "Complete Profile"})
        elif profile_pic_file:
            messages.error(request, "Uploaded file is not a valid image.")
            return render(request, "user/profile_setup.html", {"title": "Complete Profile"})

        # If any errors occurred, stop here
        if messages.get_messages(request):
            return render(request, "user/profile_setup.html", {"title": "Complete Profile"})

        # Save user data
        user = request.user
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        profile_data = {
            "bio": bio,
            "phone_no_prefix": phone_no_prefix,
            "phone_no": phone_no,
            "address": address,
            "date_of_birth": date_of_birth,
        }

        if profile_pic_path:
            profile_data["image"] = profile_pic_path

        Profile.objects.update_or_create(user=user, defaults=profile_data)

        Activity.objects.create(
            user=user,
            activity_type="Profile Setup",
            description=f"Completed profile setup for {user.username}",
        )

        messages.success(request, "Profile updated successfully.")
        return redirect("home")

    return render(request, "user/profile_setup.html", {"title": "Complete Profile"})


def check_username(request):
    username = request.GET.get("username", "").strip()

    if not username:
        return HttpResponse(
            '<span style="color: red;">❌ Username cannot be empty</span>'
        )

    if User.objects.filter(username=username).exists():
        return HttpResponse(
            '<span style="color: red;">❌ Username is already taken</span>'
        )

    return HttpResponse('<span style="color: green;"> Username is available</span>')

# profile view
@login_required
def profile(request):
    profile = request.user.profile
    return render(request, "user/profile.html", {"profile": profile})


@login_required
def update_email_request(request):
    if request.method == "POST":
        new_email = request.POST.get("new_email").strip()

        if User.objects.filter(email=new_email).exists():
            messages.error(request, "❌ This email is already in use.")
            return redirect("update_user")

        # Generate verification token
        profile = request.user.profile
        profile.email_confirmation_token = uuid.uuid4()
        profile.save()

        # Send email verification link
        confirmation_link = f"{settings.SITE_URL}/confirm-new-email/{profile.email_confirmation_token}/{new_email}/"
        if project_settings.DEBUG is False:
            try:
                send_email_using_resend(
                    to_email=new_email,
                    subject="Confirm Your New Email",
                    title="Confirm Your New Email",
                    body="Please confirm your new email address.",
                    anchor_link=confirmation_link,
                    anchor_text="Confirm New Email",
                )
            except Exception as error:
                messages.error(request,f"Error sending confirmation email: {error}")
                return redirect("update_user")
        # subject = "Confirm Your New Email"
        # from_email = "codingfoxblogs@gmail.com"
        # to = new_email
        # text_content = "Please confirm your new email."
        # html_content = f'''
        # <html lang="en">
        # <head>
        #     <meta charset="UTF-8">
        #     <meta name="viewport" content="width=device-width, initial-scale=1">
        #     <title>Email Confirmation</title>
        # </head>
        # <body style="font-family: 'Poppins', Arial, sans-serif; background: #ffffff; padding: 20px;">
        #     <h2 style="color: #0076d1;">Confirm Your New Email</h2>
        #     <p>Hello,</p>
        #     <p>Click the link below to verify and update your email address:</p>
        #     <p><a href="{confirmation_link}" style="padding: 10px; background-color: #0076d1; color: white; text-decoration: none;">Confirm New Email</a></p>
        #     <p>If you did not request this change, please ignore this email.</p>
        # </body>
        # </html>
        # '''
        # msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
        # msg.attach_alternative(html_content, "text/html")
        # msg.send()

        messages.success(
            request, "Verification email sent. Please check your new email."
        )
        return redirect("update_user")

    return redirect("update_user")


@login_required
def confirm_new_email(request, token, new_email):
    profile = get_object_or_404(Profile, email_confirmation_token=token)

    # Ensure the logged-in user is updating their email
    if profile.user != request.user:
        messages.error(request, "❌ Unauthorized request.")
        return redirect("home")

    # Update email and clear token
    profile.user.email = new_email
    profile.user.save()
    profile.email_confirmation_token = None
    profile.save()

    messages.success(request, " Your email has been updated successfully!")
    return redirect("update_user")
