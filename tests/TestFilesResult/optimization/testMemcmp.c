#include <stdbool.h>
#include <string.h>
int main()
{
  bool run = 1;
  int programStep = 1;
  char c[] = "testMemcmp";
  while (run)
  {
    if (programStep == 1)
    {
      if ((((c[0] == 't') && (c[1] == 'e')) && (c[2] == 's')) && (c[3] == 't'))
      {
        programStep = 2;
      }
      else
      {
        programStep = 3;
      }
    }
    if (programStep == 2)
    {
      return 0;
      programStep = 4;
    }
    if (programStep == 3)
    {
      return 1;
      programStep = 4;
    }
    if (programStep == 4)
    {
      run = 0;
    }
  }

}

