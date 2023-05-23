#include <stdio.h>
#include <stdbool.h>
int main()
{
  bool run = 1;
  int programStep = 1;
  int i;
  int n;
  int i_2;
  int x;
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
        i_2 = i;
        if (i <= n)
      {
        programStep = 9;
      }
      else
      {
        programStep = 7;
      }
        break;

      case 4:
        
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

      case 9:
        x = 1;
        programStep = 10;
        break;

      case 10:
        if (x <= i_2)
      {
        programStep = 11;
      }
      else
      {
        programStep = 13;
      }
        break;

      case 11:
        printf("%d ", x);
        programStep = 12;
        break;

      case 12:
        x++;
        programStep = 10;
        break;

      case 13:
      {
        programStep = 4;
      }
        break;

      case 8:
        run = 0;
        break;

    }

  }

}

