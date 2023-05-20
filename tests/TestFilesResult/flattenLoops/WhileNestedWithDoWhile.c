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
      result = result + 1;
      y++;
    }
    while (y <= 6);
    x++;
  }

  return result;
}

