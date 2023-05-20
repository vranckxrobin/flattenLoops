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
    if (programStep == 1)
    {
      if (x <= 5)
      {
        programStep = 2;
      }
      else
      {
        programStep = 7;
      }
    }
    if (programStep == 2)
    {
      y = 1;
      programStep = 3;
    }
    if (programStep == 3)
    {
      if (y <= 6)
      {
        programStep = 4;
      }
      else
      {
        programStep = 6;
      }
    }
    if (programStep == 4)
    {
      result = result + 1;
      programStep = 5;
    }
    if (programStep == 5)
    {
      y++;
      programStep = 3;
    }
    if (programStep == 6)
    {
      x++;
      programStep = 1;
    }
    if (programStep == 7)
    {
      return result;
      programStep = 8;
    }
    if (programStep == 8)
    {
      run = 0;
    }
  }

}

