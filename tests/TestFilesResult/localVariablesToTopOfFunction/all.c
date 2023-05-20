#include <stdbool.h>
int main()
{
  int b;
  int c;
  int d;
  int a = 1;
  while (a < 10)
  {
    
    b = 1;
    a = a + b;
    do
    {
      c = 1;
      b = b + c;
    }
    while (b < 10);
    if (b == 10)
    {
      d = 1;
      a = a + d;
    }
  }

  return a;
}

