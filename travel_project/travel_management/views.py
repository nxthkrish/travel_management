from django.core.mail import send_mail
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group,update_last_login
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import CustomUser, Employee, Manager, TravelRequest, Approval, AdminRequestProcessing
from .serializers import TravelRequestSerializer,UserSerializer,CustomUserSerializer
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import check_password

#creating admin views here
CustomUser = get_user_model()
@csrf_exempt  # Disable CSRF
def create_admin(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        if not username or not email or not password:
            return JsonResponse({"error": "All fields are required"}, status=400)

        admin_user = CustomUser.objects.create_user(username=username, email=email, password=password, role="admin")
        token, _ = Token.objects.get_or_create(user=admin_user)

        return JsonResponse({
            "message": "Admin created successfully",
            "token": token.key
        }, status=201)
    
@api_view(['POST'])
@permission_classes([AllowAny])  # Ensures login endpoint does not require authentication
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    try:
        # Fetch user by username
        user = CustomUser.objects.get(username=username)

        # Check if password matches
        if check_password(password, user.password):
            # Retrieve or create authentication token
            token, _ = Token.objects.get_or_create(user=user)

            return Response({
                "message": "Login successful",
                "token": token.key,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "role": user.role
                }
            })
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    except CustomUser.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


# 🔹 Add Manager/Employee (Admin Token Required)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_user(request):
    if request.user.role != 'admin':
        return Response({"error": "Only admin can add users"}, status=status.HTTP_403_FORBIDDEN)

    data = request.data
    serializer = UserSerializer(data=data)

    if serializer.is_valid():
        user, token = serializer.save()
        return Response({
            "message": f"{data['role'].capitalize()} created successfully",
            "token": token
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_employee_travel_requests(request):
    # Get the logged-in user (employee)
    employee = request.user

    # Filter travel requests by the employee's ID
    travel_requests = TravelRequest.objects.filter(employee=employee)

    # Serialize the data
    serializer = TravelRequestSerializer(travel_requests, many=True)

    # Return the serialized data
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_travel_request(request):
    # Get the logged-in user (employee)
    employee = request.user

    # Add the employee to the request data
    request.data['employee'] = employee.id

    # Validate and save the travel request
    serializer = TravelRequestSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_travel_request(request, request_id):
    try:
        # Get the travel request by ID
        travel_request = TravelRequest.objects.get(id=request_id)

        # Check if the logged-in user is the owner of the request
        if travel_request.employee != request.user:
            return Response({"error": "You are not authorized to cancel this request."}, status=status.HTTP_403_FORBIDDEN)

        # Cancel the request if it's still pending
        if travel_request.cancel_request():
            return Response({"message": "Travel request canceled successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Travel request cannot be canceled because it is not in Pending status."}, status=status.HTTP_400_BAD_REQUEST)

    except TravelRequest.DoesNotExist:
        return Response({"error": "Travel request not found."}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_travel_request(request, request_id):
    try:
        # Get the travel request by ID
        travel_request = TravelRequest.objects.get(id=request_id)

        # Check if the logged-in user is the owner of the request
        if travel_request.employee != request.user:
            return Response({"error": "You are not authorized to update this request."}, status=status.HTTP_403_FORBIDDEN)

        # Check if the request is still in Pending status
        if travel_request.status != 'Pending':
            return Response({"error": "Travel request cannot be updated because it is not in Pending status."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate and update the travel request
        serializer = TravelRequestSerializer(travel_request, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except TravelRequest.DoesNotExist:
        return Response({"error": "Travel request not found."}, status=status.HTTP_404_NOT_FOUND)

#manager views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_managed_employee_travel_requests(request):
    # Get the logged-in user
    user = request.user

    # Check if the user is a manager
    try:
        manager = Manager.objects.get(user=user)
    except Manager.DoesNotExist:
        return Response({"error": "You are not a manager."}, status=status.HTTP_403_FORBIDDEN)

    # Get all employees under the manager's supervision
    employees = manager.managed_employees.all()

    # Get travel requests for these employees
    travel_requests = TravelRequest.objects.filter(employee__in=[employee.user for employee in employees])

    # Serialize the data
    serializer = TravelRequestSerializer(travel_requests, many=True)

    # Return the serialized data
    return Response(serializer.data, status=status.HTTP_200_OK)
@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def manage_employee_travel_requests(request, employee_id):
    # Get the logged-in user
    user = request.user

    # Check if the user is a manager
    try:
        manager = Manager.objects.get(user=user)
    except Manager.DoesNotExist:
        return Response({"error": "You are not a manager."}, status=status.HTTP_403_FORBIDDEN)

    # Check if the employee exists and is under the manager's supervision
    try:
        employee = Employee.objects.get(id=employee_id, manager=manager)
    except Employee.DoesNotExist:
        return Response({"error": "Employee not found or not under your supervision."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        # Get all travel requests for the employee
        travel_requests = TravelRequest.objects.filter(employee=employee.user)
        serializer = TravelRequestSerializer(travel_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        # Update the status of a travel request
        travel_request_id = request.data.get('travel_request_id')
        action = request.data.get('action')  # approve, reject, or request_clarification

        if not travel_request_id or not action:
            return Response({"error": "Both travel_request_id and action are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            travel_request = TravelRequest.objects.get(id=travel_request_id, employee=employee.user)
        except TravelRequest.DoesNotExist:
            return Response({"error": "Travel request not found."}, status=status.HTTP_404_NOT_FOUND)

        # Perform the action based on the request
        if action == 'approve':
            success = travel_request.update_status('Approved', 'Manager')
        elif action == 'reject':
            success = travel_request.update_status('Rejected', 'Manager')
        elif action == 'request_clarification':
            success = travel_request.update_status('Clarification Requested', 'Manager')
        else:
            return Response({"error": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)

        if success:
            return Response({"message": f"Travel request {action}ed successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Travel request cannot be updated because it is not in Pending status."}, status=status.HTTP_400_BAD_REQUEST)
        


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_managed_employee_travel_requests(request):
    # Get the logged-in user
    user = request.user

    # Check if the user is a manager
    try:
        manager = Manager.objects.get(user=user)
    except Manager.DoesNotExist:
        return Response({"error": "You are not a manager."}, status=status.HTTP_403_FORBIDDEN)

    # Get all employees under the manager's supervision
    employees = manager.managed_employees.all()

    # Get query parameters for filtering and searching
    start_date = request.query_params.get('start_date')  # Filter by creation date (start range)
    end_date = request.query_params.get('end_date')  # Filter by creation date (end range)
    employee_name = request.query_params.get('employee_name')  # Search by employee name

    # Build the base query for travel requests
    travel_requests = TravelRequest.objects.filter(employee__in=[employee.user for employee in employees])

    # Apply date filtering if start_date and/or end_date are provided
    if start_date:
        travel_requests = travel_requests.filter(created_at__gte=start_date)  # Greater than or equal to start_date
    if end_date:
        travel_requests = travel_requests.filter(created_at__lte=end_date)  # Less than or equal to end_date

    # Apply employee name search if employee_name is provided
    if employee_name:
        travel_requests = travel_requests.filter(
            Q(employee__username__icontains=employee_name) |  # Search by username
            Q(employee__first_name__icontains=employee_name) |  # Search by first name
            Q(employee__last_name__icontains=employee_name)  # Search by last name
        )

    # Serialize the data
    serializer = TravelRequestSerializer(travel_requests, many=True)

    # Return the serialized data
    return Response(serializer.data, status=status.HTTP_200_OK)

#admin views
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_status(request, user_id):
    # Check if the logged-in user is an admin
    if not request.user.is_superuser:
        return Response({"error": "Only admin can update user status."}, status=status.HTTP_403_FORBIDDEN)

    # Get the user to update
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    # Validate and update the status
    serializer = CustomUserSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": f"User status updated to {serializer.data['status']}."}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def admin_manage_travel_requests(request, request_id=None):
    # Check if the logged-in user is an admin
    if not request.user.is_superuser:
        return Response({"error": "Only admin can access this endpoint."}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        # Get all travel requests
        travel_requests = TravelRequest.objects.all()
        serializer = TravelRequestSerializer(travel_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        # Perform actions on a specific travel request
        if not request_id:
            return Response({"error": "Travel request ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            travel_request = TravelRequest.objects.get(id=request_id)
        except TravelRequest.DoesNotExist:
            return Response({"error": "Travel request not found."}, status=status.HTTP_404_NOT_FOUND)

        action = request.data.get('action')  # close, request_clarification
        clarification_details = request.data.get('clarification_details', '')

        if action == 'close':
            success = travel_request.close_request(updated_by='Admin')
            if success:
                return Response({"message": "Travel request closed successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Travel request cannot be closed because it is not approved."}, status=status.HTTP_400_BAD_REQUEST)

        elif action == 'request_clarification':
            success = travel_request.request_clarification(updated_by='Admin', clarification_details=clarification_details)
            if success:
                return Response({"message": "Clarification requested successfully."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Travel request cannot be updated because it is not pending or rejected."}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({"error": "Invalid action."}, status=status.HTTP_400_BAD_REQUEST)
        
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def admin_request_email(request, request_id):
    """Send an email to request additional information about a travel request from admin."""
    # Ensure the logged-in user is an admin
    if request.user.role != 'admin':
        return Response({"error": "Only admin can send email requests."}, status=status.HTTP_403_FORBIDDEN)

    # Get the travel request object
    travel_request = get_object_or_404(TravelRequest, id=request_id)

    # Ensure the request has a linked employee
    if not travel_request.employee:
        return Response({"error": "Travel request is not linked to an employee."}, status=status.HTTP_400_BAD_REQUEST)

    # Get the employee's email
    recipient_email = travel_request.employee.email

    # Get additional request details from the request data
    additional_request = request.data.get("additional_requests")
    if not additional_request:
        return Response({"error": "Additional request details are required."}, status=status.HTTP_400_BAD_REQUEST)

    # Update the travel request object
    travel_request.additional_requests = additional_request
    travel_request.resubmitted = True
    travel_request.save()

    # Send the email
    subject = "Additional Information Requested for Your Travel Request"
    message = (
        f"Dear {travel_request.employee.username},\n\n"
        f"We need more details regarding your travel request (ID: {travel_request.id}).\n\n"
        f"Additional Request: {additional_request}\n\n"
        f"Please provide the requested information at your earliest convenience.\n\n"
        f"Best Regards,\nYour Admin Team"
    )

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[recipient_email],
            fail_silently=False,
        )
        return Response({"message": "Additional request added and email sent successfully."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": f"Email failed to send. Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)