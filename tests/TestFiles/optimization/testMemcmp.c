#include <stdbool.h>
#include <string.h>
int main()
{
  bool run = 1;
  int programStep = 1;
  char c[] = "testMemcmp";
  while (run)
  {
    switch (programStep)
    {
      case 1:
        if (memcmp(c, "test", 4) == 0)
        {
          programStep = 2;
        }
        else
        {
          programStep = 3;
        }
        break;

      case 2:
        return 0;
        programStep = 4;
        break;

      case 3:
        return 1;
        programStep = 4;
        break;

      case 4:
        run = 0;
        break;

    }

  }

}

