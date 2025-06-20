from rest_framework.exceptions import PermissionDenied,NotFound
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import status
from .serializers import *
from .models import *
from .tasks import *




#For test
class HelloViewSet(viewsets.ViewSet):
    def list(self, request):
        return Response({"message": "Hello from the API!"})
    

#For Register
class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#For login
class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#For Ideas
class IdeaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = IdeaSerializer

    def get_queryset(self):
        user = self.request.user
        # Reviewers see all ideas
        if user.groups.filter(name='Reviewer').exists():
            return Idea.objects.filter(reviwed_by=user)
        # Regular users only see their own ideas
        return Idea.objects.filter(submitted_by=user)

    def perform_create(self, serializer):
        serializer.save(submitted_by=self.request.user)


class OrganizerViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OrganizerSerializer
    
    def get_queryset(self):
        return Organizer.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.groups.filter(name='organizer').exists():
            return Event.objects.filter(organizer__user=user)
        
        return Event.objects.all()


    def perform_create(self, serializer):
        user = self.request.user

        # Only organizers can create
        if not user.groups.filter(name='organizer').exists():
            raise PermissionDenied("Only users in the 'organizer' group can create events.")

        try:
            organizer = Organizer.objects.get(user=user)
        except Organizer.DoesNotExist:
            raise PermissionDenied("You must register as an organizer first.")

        # Optional: add checks for approval or block status
        if not organizer.is_approved:
            raise PermissionDenied("Your organizer profile is not approved yet.")
        if organizer.is_blocked:
            raise PermissionDenied("Your organizer profile is blocked.")

        serializer.save(organizer=organizer)


class EventPriceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = EventPrice.objects.all()
    serializer_class = EventPriceSerializer

    def perform_create(self, serializer):
        user = self.request.user
        event_id = self.request.query_params.get('event')  # e.g. ?event=4

        if not event_id:
            raise PermissionDenied("Event ID must be provided as a query parameter.")

        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            raise NotFound("Event not found.")

        if event.organizer.user != user:
            raise PermissionDenied("You are not the owner of this event.")

        serializer.save(event=event)


class TicketViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.groups.filter(name='organizer').exists():
            return Ticket.objects.filter(event__event__organizer__user=user)
        else:
            return Ticket.objects.filter(user=user)


    def perform_create(self, serializer):
        user = self.request.user
        event_price = serializer.validated_data.get('event')  # EventPrice instance

        if not event_price:
            raise PermissionDenied("Event must be provided.")

        # Check only if user is in 'organizer' group
        if user.groups.filter(name='organizer').exists():
            if event_price.event.organizer.user == user:
                raise PermissionDenied("Organizers cannot book tickets for their own events.")

        serializer.save(user=user)


from django.shortcuts import render
def index(request):
    return render(request, "webrtcapp/index.html")