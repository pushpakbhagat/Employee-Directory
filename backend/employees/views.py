from django.shortcuts import render
from django.db.models import Count, ProtectedError
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Department, Employee, LeaveRequest
from .serializers import DepartmentSerializer, EmployeeSerializer, LeaveRequestSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.annotate(employee_count=Count('employees'))
    serializer_class = DepartmentSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {'detail': 'Cannot delete a department that still has employees.'},
                status=status.HTTP_400_BAD_REQUEST,
            )


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.select_related('department')
    serializer_class = EmployeeSerializer


class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.select_related('employee')
    serializer_class = LeaveRequestSerializer

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        leave = self.get_object()
        leave.status = LeaveRequest.Status.APPROVED
        leave.save()
        return Response(self.get_serializer(leave).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        leave = self.get_object()
        leave.status = LeaveRequest.Status.REJECTED
        leave.save()
        return Response(self.get_serializer(leave).data)