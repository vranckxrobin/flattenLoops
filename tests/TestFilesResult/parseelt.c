#include <string.h>
#include "minixml.h"
#include <stdbool.h>
static void parseelt(struct xmlparser *p)
{
  bool run = 1;
  int programStep = 1;
  const char *data;
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
        programStep = 51;
      }
        break;

      case 2:
        if (((p->xml + 4) <= p->xmlend) && (0 == memcmp(p->xml, "<!--", 4)))
      {
        programStep = 3;
      }
      else
      {
        programStep = 8;
      }
        break;

      case 3:
        p->xml += 3;
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
        p->xml += 3;
        programStep = 1;
        break;

      case 8:
        if ((p->xml[0] == '<') && (p->xml[1] != '?'))
      {
        programStep = 9;
      }
      else
      {
        programStep = 50;
      }
        break;

      case 9:
        i = 0;
        elementname = ++p->xml;
        programStep = 10;
        break;

      case 10:
        if (((!(((((*p->xml) == ' ') || ((*p->xml) == '\t')) || ((*p->xml) == '\r')) || ((*p->xml) == '\n'))) && ((*p->xml) != '>')) && ((*p->xml) != '/'))
      {
        programStep = 11;
      }
      else
      {
        programStep = 16;
      }
        break;

      case 11:
        i++;
        programStep = 12;
        break;

      case 12:
        p->xml++;
        programStep = 13;
        break;

      case 13:
        if (p->xml >= p->xmlend)
      {
        return;
      }
      else
      {
        programStep = 14;
      }
        break;

      case 14:
        if ((*p->xml) == ':')
      {
        programStep = 15;
      }
      else
      {
        programStep = 10;
      }
        break;

      case 15:
        i = 0;
        elementname = ++p->xml;
        programStep = 10;
        break;

      case 16:
        if (i > 0)
      {
        programStep = 17;
      }
      else
      {
        programStep = 41;
      }
        break;

      case 17:
        if (p->starteltfunc)
      {
        p->starteltfunc(p->data, elementname, i);
      }
        programStep = 18;
        break;

      case 18:
        if (parseatt(p))
      {
        return;
      }
      else
      {
        programStep = 19;
      }
        break;

      case 19:
        if ((*p->xml) != '/')
      {
        programStep = 20;
      }
      else
      {
        programStep = 1;
      }
        break;

      case 20:
        
        i = 0;
        data = ++p->xml;
        programStep = 21;
        break;

      case 21:
        if (p->xml >= p->xmlend)
      {
        return;
      }
      else
      {
        programStep = 22;
      }
        break;

      case 22:
        if (((((*p->xml) == ' ') || ((*p->xml) == '\t')) || ((*p->xml) == '\r')) || ((*p->xml) == '\n'))
      {
        programStep = 23;
      }
      else
      {
        programStep = 26;
      }
        break;

      case 23:
        i++;
        programStep = 24;
        break;

      case 24:
        p->xml++;
        programStep = 25;
        break;

      case 25:
        if (p->xml >= p->xmlend)
      {
        return;
      }
      else
      {
        programStep = 22;
      }
        break;

      case 26:
        if ((p->xmlend >= (p->xml + (9 + 3))) && (memcmp(p->xml, "<![CDATA[", 9) == 0))
      {
        programStep = 27;
      }
      else
      {
        programStep = 36;
      }
        break;

      case 27:
        p->xml += 9;
        data = p->xml;
        i = 0;
        programStep = 28;
        break;

      case 28:
        if (memcmp(p->xml, "]]>", 3) != 0)
      {
        programStep = 29;
      }
      else
      {
        programStep = 32;
      }
        break;

      case 29:
        i++;
        programStep = 30;
        break;

      case 30:
        p->xml++;
        programStep = 31;
        break;

      case 31:
        if ((p->xml + 3) >= p->xmlend)
      {
        return;
      }
      else
      {
        programStep = 28;
      }
        break;

      case 32:
        if ((i > 0) && p->datafunc)
      {
        p->datafunc(p->data, data, i);
      }
        programStep = 33;
        break;

      case 33:
        if ((*p->xml) != '<')
      {
        programStep = 34;
      }
      else
      {
        programStep = 1;
      }
        break;

      case 34:
        p->xml++;
        programStep = 35;
        break;

      case 35:
        if (p->xml >= p->xmlend)
      {
        return;
      }
      else
      {
        programStep = 33;
      }
        break;

      case 36:
        if ((*p->xml) != '<')
      {
        programStep = 37;
      }
      else
      {
        programStep = 40;
      }
        break;

      case 37:
        i++;
        programStep = 38;
        break;

      case 38:
        p->xml++;
        programStep = 39;
        break;

      case 39:
        if ((p->xml + 1) >= p->xmlend)
      {
        return;
      }
      else
      {
        programStep = 36;
      }
        break;

      case 40:
        if (((i > 0) && p->datafunc) && ((*(p->xml + 1)) == '/'))
      {
        p->datafunc(p->data, data, i);
      }
        programStep = 1;
        break;

      case 41:
        if ((*p->xml) == '/')
      {
        programStep = 42;
      }
      else
      {
        programStep = 1;
      }
        break;

      case 42:
        i = 0;
        elementname = ++p->xml;
        programStep = 43;
        break;

      case 43:
        if (p->xml >= p->xmlend)
      {
        return;
      }
      else
      {
        programStep = 44;
      }
        break;

      case 44:
        if ((*p->xml) != '>')
      {
        programStep = 45;
      }
      else
      {
        programStep = 48;
      }
        break;

      case 45:
        i++;
        programStep = 46;
        break;

      case 46:
        p->xml++;
        programStep = 47;
        break;

      case 47:
        if (p->xml >= p->xmlend)
      {
        return;
      }
      else
      {
        programStep = 44;
      }
        break;

      case 48:
        if (p->endeltfunc)
      {
        p->endeltfunc(p->data, elementname, i);
      }
        programStep = 49;
        break;

      case 49:
        p->xml++;
        programStep = 1;
        break;

      case 50:
        p->xml++;
        programStep = 1;
        break;

      case 51:
        run = 0;
        break;

    }

  }

}

