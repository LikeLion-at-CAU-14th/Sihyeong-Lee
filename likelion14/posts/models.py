from django.db import models
from accounts.models import User

# Create your models here.
class BaseModel(models.Model): # models.Model을 상속받음
    created_at = models.DateTimeField(auto_now_add=True) # 객체를 생성할 때 날짜와 시간 저장
    updated_at = models.DateTimeField(auto_now=True) # 객체를 저장할 때 날짜와 시간 갱신

    class Meta:
        abstract = True


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField()

    def __str__(self):
        return self.name
    
class Post(BaseModel): # BaseModel을 상속받음

    CHOICES = (
        ('STORED', '보관'),
        ('PUBLISHED', '발행')
    )

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50)
    content = models.TextField()
    status = models.CharField(max_length=10, choices=CHOICES, default='STORED')
    writer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='post')
    category = models.ManyToManyField(Category, related_name='posts')

    def __str__(self):
        return self.title

    #게시물도 여러 카테고리 선택 가능, 카테고리도 여러 게시물 선택 가능
    #-> 다대다관계 -> 게시글 삭제되도 카테고리는 삭제x
    #models.ManyToManyField를 통해 다대다 관계를 했더니 db.sqlite3에 'posts_category_post' 테이블이 자동으로 생성
    #->다대다관계를 일대다, 다대일로 자동 전환됨
    
class Comment(BaseModel): # BaseModel을 상속받음 -> 작성 시간, 수정 시간 저장
    id = models.AutoField(primary_key=True)
    content = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')

    def __str__(self):
        return f"{self.post.title}의 댓글: {self.content}"
    #post를 참조하면서 게시글이 삭제되면 댓글도 삭제 + 다대일 참조로 여러 댓글 가능