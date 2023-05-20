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
        programStep = 10;
      }
        break;

      case 2:
        if ((p->xml[0] == '<') && (p->xml[1] != '?'))
      {
        programStep = 3;
      }
      else
      {
        programStep = 1;
      }
        break;

      case 3:
        i = 0;
        elementname = ++p->xml;
        programStep = 4;
        break;

      case 4:
        if (((*p->xml) != '>') && ((*p->xml) != '/'))
      {
        programStep = 5;
      }
      else
      {
        programStep = 8;
      }
        break;

      case 5:
        i++;
        programStep = 6;
        break;

      case 6:
        p->xml++;
        programStep = 7;
        break;

      case 7:
        if (p->xml >= p->xmlend)
      {
        return;
      }
      else
      {
        programStep = 4;
      }
        break;

      case 8:
        if (i > 0)
      {
        programStep = 9;
      }
      else
      {
        programStep = 1;
      }
        break;

      case 9:
        elementname = "3";
        programStep = 1;
        break;

      case 10:
        run = 0;
        break;

    }

  }

}

