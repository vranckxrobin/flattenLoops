#include <stdbool.h>
static void parseelt(struct xmlparser *p)
{
  bool run = 1;
  int programStep = 1;
  int i;
  const char *elementname;
  while (run)
  {
    switch (programStep)
    {
      case 1:
        if (p->xml < (p->xmlend - 1))
      {
        programStep = 2;
      }
      else
      {
        programStep = 8;
      }
        break;

      case 2:
        if (((p->xml + 4) <= p->xmlend) && (0 == memcmp(p->xml, "<!--", 4)))
      {
        programStep = 3;
      }
      else
      {
        programStep = 1;
      }
        break;

      case 3:
        p->xml += 3;
        p->xml += 4;
        programStep = 4;
        break;

      case 4:
        p->xml++;
        programStep = 5;
        break;

      case 5:
        if ((p->xml + 3) >= p->xmlend)
      {
        return;
      }
      else
      {
        programStep = 6;
      }
        break;

      case 6:
        if (memcmp(p->xml, "-->", 3) != 0)
      {
        programStep = 4;
      }
      else
      {
        programStep = 7;
      }
        break;

      case 7:
        p->xml += 1;
        programStep = 1;
        break;

      case 8:
        run = 0;
        break;

    }

  }

}

