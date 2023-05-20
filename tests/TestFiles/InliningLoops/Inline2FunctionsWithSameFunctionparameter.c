#include <stdio.h>
#include <stdbool.h>
void func2(int i)
{
  bool run = 1;
  int programStep = 1;
  int x;
  while (run)
  {
    switch (programStep)
    {
      case 1:
        x = 1;
        programStep = 2;
        break;

      case 2:
        if (x <= i)
      {
        programStep = 3;
      }
      else
      {
        programStep = 5;
      }
        break;

      case 3:
        printf("%d ", x);
        programStep = 4;
        break;

      case 4:
        x++;
        programStep = 2;
        break;

      case 5:
        run = 0;
        break;

    }

  }

}

int main()
{
  bool run = 1;
  int programStep = 1;
  int i;
  int n;
  while (run)
  {
    switch (programStep)
    {
      case 1:
        i = 1;
        programStep = 2;
        break;

      case 2:
        n = 6;
        programStep = 3;
        break;

      case 3:
        if (i <= n)
      {
        programStep = 4;
      }
      else
      {
        programStep = 7;
      }
        break;

      case 4:
        func2(i);
        programStep = 5;
        break;

      case 5:
        printf("\n");
        programStep = 6;
        break;

      case 6:
        i++;
        programStep = 3;
        break;

      case 7:
        return 0;
        programStep = 8;
        break;

      case 8:
        run = 0;
        break;

    }

  }

}

