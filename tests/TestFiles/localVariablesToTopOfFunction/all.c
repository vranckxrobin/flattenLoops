int main()  
{  
    int a=1;
    while (a<10){
      int b;
      b=1;
      a=a+b;
      do{
        int c=1;
        b=b+c;
      }while (b<10);
      if(b==10){
        int d=1;
        a=a+d;
      }
    }  
    return a;
}  