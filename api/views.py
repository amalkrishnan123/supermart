from django.shortcuts import render
from adminapp.models import Category,Product
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import Category_serial,Product_serial
from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import get_object_or_404

# Create your views here.
@api_view(['GET',"POST","PUT","PATCH",'DELETE'])
def category_api(request):
    if request.method=='GET':
        cat=Category.objects.all()
        serial=Category_serial(cat,many=True)
        return Response(serial.data)
    elif request.method=='POST':
        data=request.data
        serial=Category_serial(data=data)
        if serial.is_valid():
            serial.save()
            return Response(serial.data)
        else:
            return Response(serial.errors)
    elif request.method=='PUT':
        data=request.data
        cat=Category.objects.get(id=data['id'])
        serail=Category_serial(cat,data=data,partial=False)
        if serail.is_valid():
            serail.save()
            return Response(serail.data)
    elif request.method=='PATCH':
        data=request.data
        cat=Category.objects.get(id=data['id'])
        serail=Category_serial(cat,data=data,partial=True)
        if serail.is_valid():
            serail.save()
            return Response(serail.data)
    else:
        data=request.data
        cat=Category.objects.get(id=data['id'])
        cat.delete()
        return Response({'message':'deleted successfully'})
    
    
@api_view(['GET','POST','PUT','PATCH','DELETE'])
def product_api(request):
    if request.method=='GET':
        cat=Product.objects.all()
        serial=Product_serial(cat,many=True)
        return Response(serial.data)
    elif request.method=='POST':
        data=request.data
        serial=Product_serial(data=data)
        if serial.is_valid():
            serial.save()
            return Response(serial.data)
        else:
            return Response(serial.errors)
    elif request.method=='PUT':
        data=request.data
        cat=Product.objects.get(id=data['id'])
        serail=Product_serial(cat,data=data,partial=False)
        if serail.is_valid():
            serail.save()
            return Response(serail.data)
    elif request.method=='PATCH':
        data=request.data
        cat=Product.objects.get(id=data['id'])
        serail=Product_serial(cat,data=data,partial=True)
        if serail.is_valid():
            serail.save()
            return Response(serail.data)
    else:
        data=request.data
        cat=Product.objects.get(id=data['id'])
        cat.delete()
        return Response({'message':'deleted successfully'})

#class based view
class Category_list(APIView):
    def get(self,request):
        cat=Category.objects.all()
        serial=Category_serial(cat,many=True)
        return Response(serial.data)
    def post(self,request):
        serial=Category_serial(data=request.data)
        if serial.is_valid():
            serial.save()
            return Response(serial.data,status=status.HTTP_201_CREATED)
        return Response(serial.errors, status=status.HTTP_400_BAD_REQUEST)
class Category_alter(APIView):
#to edit,delete we need to pass id,so we need to create a separate class to pass id
    def put(self,request,pk):
        cat=Category.objects.get(id=pk)
        serial=Category_serial(cat,data=request.data)
        if serial.is_valid():
            serial.save()
            return Response(serial.data)
        return Response(serial.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self,request,pk):
        cat=Category.objects.get(id=pk)
        cat.delete()
        return Response({"message": "Category deleted successfully"},status=status.HTTP_204_NO_CONTENT)
    
class Product_view(APIView):
    def post(self,request):
        serial=Product_serial(data=request.data)
        if serial.is_valid():
            serial.save()
            return Response(serial.data,status=status.HTTP_201_CREATED)
        return Response(serial.errors, status=status.HTTP_400_BAD_REQUEST)

class Product_alter(APIView):
# i use get method here because im passingf the pk for specific product.the post method dont need pk.
    def get(self,request,pk):
        pro=get_object_or_404(Product,id=pk)
        serial=Product_serial(pro)
        return Response(serial.data)
    def put(self,request,pk):
        pro=get_object_or_404(Product,id=pk)
        serial=Product_serial(pro,data=request.data)
        if serial.is_valid():
            serial.save()
            return Response(serial.data)
        return Response(serial.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self,request,pk):
        pro=get_object_or_404(Product,id=pk)
        pro.delete()
        return Response({"message": "Category deleted successfully"},status=status.HTTP_204_NO_CONTENT)

        


