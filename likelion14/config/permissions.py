from rest_framework.permissions import BasePermission

class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        # 읽기 권한은 모든 사용자에게 허용
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        # 쓰기 권한은 객체의 소유자에게만 허용
        return obj.writer == request.user
    
class Isdaytime(BasePermission): #7시부터 22시까지만 접근 허용하는 권한 클래스
    def has_permission(self, request, view):
        from datetime import datetime
        now = datetime.now().time()
        return now.hour >= 7 and now.hour < 22