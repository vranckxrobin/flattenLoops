#include <string.h>
#include "minixml.h"
#include <stdbool.h>
static int parseatt(struct xmlparser *p)
{
  bool run = 1;
  int programStep = 1;
  char sep;
  const char *attname;
  int attnamelen;
  const char *attvalue;
  int attvaluelen;
  while (run)
  {
    switch (programStep)
    {
      case 1:
        if (p->xml < p->xmlend)
      {
        programStep = 2;
      }
      else
      {
        programStep = 30;
      }
        break;

      case 2:
        if (((*p->xml) == '/') || ((*p->xml) == '>'))
      {
        return 0;
      }
      else
      {
        programStep = 3;
      }
        break;

      case 3:
        if (!(((((*p->xml) == ' ') || ((*p->xml) == '\t')) || ((*p->xml) == '\r')) || ((*p->xml) == '\n')))
      {
        programStep = 4;
      }
      else
      {
        programStep = 29;
      }
        break;

      case 4:
        
        attname = p->xml;
        attnamelen = 0;
        programStep = 5;
        break;

      case 5:
        if (((*p->xml) != '=') && (!(((((*p->xml) == ' ') || ((*p->xml) == '\t')) || ((*p->xml) == '\r')) || ((*p->xml) == '\n'))))
      {
        programStep = 6;
      }
      else
      {
        programStep = 9;
      }
        break;

      case 6:
        attnamelen++;
        programStep = 7;
        break;

      case 7:
        p->xml++;
        programStep = 8;
        break;

      case 8:
        if (p->xml >= p->xmlend)
      {
        return -1;
      }
      else
      {
        programStep = 5;
      }
        break;

      case 9:
        if ((*(p->xml++)) != '=')
      {
        programStep = 10;
      }
      else
      {
        programStep = 11;
      }
        break;

      case 10:
        if (p->xml >= p->xmlend)
      {
        return -1;
      }
      else
      {
        programStep = 9;
      }
        break;

      case 11:
        if (((((*p->xml) == ' ') || ((*p->xml) == '\t')) || ((*p->xml) == '\r')) || ((*p->xml) == '\n'))
      {
        programStep = 12;
      }
      else
      {
        programStep = 14;
      }
        break;

      case 12:
        p->xml++;
        programStep = 13;
        break;

      case 13:
        if (p->xml >= p->xmlend)
      {
        return -1;
      }
      else
      {
        programStep = 11;
      }
        break;

      case 14:
        sep = *p->xml;
        programStep = 15;
        break;

      case 15:
        if ((sep == '\'') || (sep == '\"'))
      {
        programStep = 16;
      }
      else
      {
        programStep = 23;
      }
        break;

      case 16:
        p->xml++;
        programStep = 17;
        break;

      case 17:
        if (p->xml >= p->xmlend)
      {
        return -1;
      }
      else
      {
        programStep = 18;
      }
        break;

      case 18:
        attvalue = p->xml;
        attvaluelen = 0;
        programStep = 19;
        break;

      case 19:
        if ((*p->xml) != sep)
      {
        programStep = 20;
      }
      else
      {
        programStep = 28;
      }
        break;

      case 20:
        attvaluelen++;
        programStep = 21;
        break;

      case 21:
        p->xml++;
        programStep = 22;
        break;

      case 22:
        if (p->xml >= p->xmlend)
      {
        return -1;
      }
      else
      {
        programStep = 19;
      }
        break;

      case 23:
        attvalue = p->xml;
        attvaluelen = 0;
        programStep = 24;
        break;

      case 24:
        if (((!(((((*p->xml) == ' ') || ((*p->xml) == '\t')) || ((*p->xml) == '\r')) || ((*p->xml) == '\n'))) && ((*p->xml) != '>')) && ((*p->xml) != '/'))
      {
        programStep = 25;
      }
      else
      {
        programStep = 28;
      }
        break;

      case 25:
        attvaluelen++;
        programStep = 26;
        break;

      case 26:
        p->xml++;
        programStep = 27;
        break;

      case 27:
        if (p->xml >= p->xmlend)
      {
        return -1;
      }
      else
      {
        programStep = 24;
      }
        break;

      case 28:
        if (p->attfunc)
      {
        p->attfunc(p->data, attname, attnamelen, attvalue, attvaluelen);
      }
        programStep = 29;
        break;

      case 29:
        p->xml++;
        programStep = 1;
        break;

      case 30:
        return -1;
        programStep = 31;
        break;

      case 31:
        run = 0;
        break;

    }

  }

}

