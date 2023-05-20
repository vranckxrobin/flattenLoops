#include <stdbool.h>
int main()
{
  int x = 1;
  int y;
  int result = 0;
  while (x <= 5)
  {
    y = 1;
    do
    {
      if (result < 20)
      {
        result = result + 1;
      }
      y++;
    }
    while (y <= 6);
    x++;
  }

  if (result == 20)
  {
    return 0;
  }
  else
  {
    return 1;
  }
}

