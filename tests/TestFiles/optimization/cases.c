#include <stdbool.h>
int main()
{
  bool run = 1;
  int programStep = 1;
  int x = 1;
  int y;
  int result = 0;
  while (run)
  {
    switch (programStep)
    {
      case 1:
        if (x <= 5)
      {
        programStep = 2;
      }
      else
      {
        programStep = 7;
      }
        break;

      case 2:
        y = 1;
        programStep = 3;
        break;

      case 3:
        if (y <= 6)
      {
        programStep = 4;
      }
      else
      {
        programStep = 6;
      }
        break;

      case 4:
        result = result + 1;
        programStep = 5;
        break;

      case 5:
        y++;
        programStep = 3;
        break;

      case 6:
        x++;
        programStep = 1;
        break;

      case 7:
        return result;
        programStep = 8;
        break;

      case 8:
        run = 0;
        break;

    }

  }

}

