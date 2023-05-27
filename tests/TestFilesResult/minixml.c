#include <string.h>
#include "minixml.h"
#include <stdbool.h>
void parsexml(struct xmlparser *parser)
{
  bool run = 1;
  int programStep = 1;
  struct xmlparser *p;
  const char *data;
  int i;
  const char *elementname;
  int parseatt;
  struct xmlparser *p_2;
  char sep;
  const char *attname;
  int attnamelen;
  const char *attvalue;
  int attvaluelen;
  while (run)
  {
    if (programStep == 1)
    {
      parser->xml = parser->xmlstart;
      programStep = 2;
    }
    if (programStep == 2)
    {
      parser->xmlend = parser->xmlstart + parser->xmlsize;
      p = parser;
      programStep = 5;
    }
    if (programStep == 3)
    {
      
      programStep = 4;
    }
    if (programStep == 5)
    {
      if (p->xml < (p->xmlend - 1))
      {
        programStep = 6;
      }
      else
      {
        programStep = 55;
      }
    }
    if (programStep == 6)
    {
      if (((p->xml + 4) <= p->xmlend) && ((((p->xml[0] == '<') && (p->xml[1] == '!')) && (p->xml[2] == '-')) && (p->xml[3] == '-')))
      {
        programStep = 7;
      }
      else
      {
        programStep = 12;
      }
    }
    if (programStep == 7)
    {
      p->xml += 3;
      programStep = 8;
    }
    if (programStep == 8)
    {
      p->xml++;
      programStep = 9;
    }
    if (programStep == 9)
    {
      if ((p->xml + 3) >= p->xmlend)
      {
        {
          programStep = 3;
        }
      }
      else
      {
        programStep = 10;
      }
    }
    if (programStep == 10)
    {
      if (((p->xml[0] == '-') && (p->xml[1] == '-')) && (p->xml[2] == '>'))
      {
        programStep = 8;
      }
      else
      {
        programStep = 11;
      }
    }
    if (programStep == 11)
    {
      p->xml += 3;
      programStep = 5;
    }
    if (programStep == 12)
    {
      if ((p->xml[0] == '<') && (p->xml[1] != '?'))
      {
        programStep = 13;
      }
      else
      {
        programStep = 54;
      }
    }
    if (programStep == 13)
    {
      i = 0;
      elementname = ++p->xml;
      programStep = 14;
    }
    if (programStep == 14)
    {
      if (((!(((((*p->xml) == ' ') || ((*p->xml) == '\t')) || ((*p->xml) == '\r')) || ((*p->xml) == '\n'))) && ((*p->xml) != '>')) && ((*p->xml) != '/'))
      {
        programStep = 15;
      }
      else
      {
        programStep = 20;
      }
    }
    if (programStep == 15)
    {
      i++;
      programStep = 16;
    }
    if (programStep == 16)
    {
      p->xml++;
      programStep = 17;
    }
    if (programStep == 17)
    {
      if (p->xml >= p->xmlend)
      {
        {
          programStep = 3;
        }
      }
      else
      {
        programStep = 18;
      }
    }
    if (programStep == 18)
    {
      if ((*p->xml) == ':')
      {
        programStep = 19;
      }
      else
      {
        programStep = 14;
      }
    }
    if (programStep == 19)
    {
      i = 0;
      elementname = ++p->xml;
      programStep = 14;
    }
    if (programStep == 20)
    {
      if (i > 0)
      {
        programStep = 21;
      }
      else
      {
        programStep = 45;
      }
    }
    if (programStep == 21)
    {
      if (p->starteltfunc)
      {
        p->starteltfunc(p->data, elementname, i);
      }
      else
      {
        
      }
      p_2 = p;
      programStep = 56;
    }
    if (programStep == 22)
    {
      if (parseatt)
      {
        {
          programStep = 3;
        }
      }
      else
      {
        programStep = 23;
      }
    }
    if (programStep == 23)
    {
      if ((*p->xml) != '/')
      {
        programStep = 24;
      }
      else
      {
        programStep = 5;
      }
    }
    if (programStep == 24)
    {
      
      i = 0;
      data = ++p->xml;
      programStep = 25;
    }
    if (programStep == 25)
    {
      if (p->xml >= p->xmlend)
      {
        {
          programStep = 3;
        }
      }
      else
      {
        programStep = 26;
      }
    }
    if (programStep == 26)
    {
      if (((((*p->xml) == ' ') || ((*p->xml) == '\t')) || ((*p->xml) == '\r')) || ((*p->xml) == '\n'))
      {
        programStep = 27;
      }
      else
      {
        programStep = 30;
      }
    }
    if (programStep == 27)
    {
      i++;
      programStep = 28;
    }
    if (programStep == 28)
    {
      p->xml++;
      programStep = 29;
    }
    if (programStep == 29)
    {
      if (p->xml >= p->xmlend)
      {
        {
          programStep = 3;
        }
      }
      else
      {
        programStep = 26;
      }
    }
    if (programStep == 30)
    {
      if ((p->xmlend >= (p->xml + (9 + 3))) && (((((((((p->xml[0] == '<') && (p->xml[1] == '!')) && (p->xml[2] == '[')) && (p->xml[3] == 'C')) && (p->xml[4] == 'D')) && (p->xml[5] == 'A')) && (p->xml[6] == 'T')) && (p->xml[7] == 'A')) && (p->xml[8] == '[')))
      {
        programStep = 31;
      }
      else
      {
        programStep = 40;
      }
    }
    if (programStep == 31)
    {
      p->xml += 9;
      data = p->xml;
      i = 0;
      programStep = 32;
    }
    if (programStep == 32)
    {
      if (((p->xml[0] == ']') && (p->xml[1] == ']')) && (p->xml[2] == '>'))
      {
        programStep = 33;
      }
      else
      {
        programStep = 36;
      }
    }
    if (programStep == 33)
    {
      i++;
      programStep = 34;
    }
    if (programStep == 34)
    {
      p->xml++;
      programStep = 35;
    }
    if (programStep == 35)
    {
      if ((p->xml + 3) >= p->xmlend)
      {
        {
          programStep = 3;
        }
      }
      else
      {
        programStep = 32;
      }
    }
    if (programStep == 36)
    {
      if ((i > 0) && p->datafunc)
      {
        p->datafunc(p->data, data, i);
      }
      else
      {
        
      }
      programStep = 37;
    }
    if (programStep == 37)
    {
      if ((*p->xml) != '<')
      {
        programStep = 38;
      }
      else
      {
        programStep = 5;
      }
    }
    if (programStep == 38)
    {
      p->xml++;
      programStep = 39;
    }
    if (programStep == 39)
    {
      if (p->xml >= p->xmlend)
      {
        {
          programStep = 3;
        }
      }
      else
      {
        programStep = 37;
      }
    }
    if (programStep == 40)
    {
      if ((*p->xml) != '<')
      {
        programStep = 41;
      }
      else
      {
        programStep = 44;
      }
    }
    if (programStep == 41)
    {
      i++;
      programStep = 42;
    }
    if (programStep == 42)
    {
      p->xml++;
      programStep = 43;
    }
    if (programStep == 43)
    {
      if ((p->xml + 1) >= p->xmlend)
      {
        {
          programStep = 3;
        }
      }
      else
      {
        programStep = 40;
      }
    }
    if (programStep == 44)
    {
      if (((i > 0) && p->datafunc) && ((*(p->xml + 1)) == '/'))
      {
        p->datafunc(p->data, data, i);
      }
      else
      {
        
      }
      programStep = 5;
    }
    if (programStep == 45)
    {
      if ((*p->xml) == '/')
      {
        programStep = 46;
      }
      else
      {
        programStep = 5;
      }
    }
    if (programStep == 46)
    {
      i = 0;
      elementname = ++p->xml;
      programStep = 47;
    }
    if (programStep == 47)
    {
      if (p->xml >= p->xmlend)
      {
        {
          programStep = 3;
        }
      }
      else
      {
        programStep = 48;
      }
    }
    if (programStep == 48)
    {
      if ((*p->xml) != '>')
      {
        programStep = 49;
      }
      else
      {
        programStep = 52;
      }
    }
    if (programStep == 49)
    {
      i++;
      programStep = 50;
    }
    if (programStep == 50)
    {
      p->xml++;
      programStep = 51;
    }
    if (programStep == 51)
    {
      if (p->xml >= p->xmlend)
      {
        {
          programStep = 3;
        }
      }
      else
      {
        programStep = 48;
      }
    }
    if (programStep == 52)
    {
      if (p->endeltfunc)
      {
        p->endeltfunc(p->data, elementname, i);
      }
      else
      {
        
      }
      programStep = 53;
    }
    if (programStep == 53)
    {
      p->xml++;
      programStep = 5;
    }
    if (programStep == 54)
    {
      p->xml++;
      programStep = 5;
    }
    if (programStep == 56)
    {
      if (p_2->xml < p_2->xmlend)
      {
        programStep = 57;
      }
      else
      {
        programStep = 85;
      }
    }
    if (programStep == 57)
    {
      if (((*p_2->xml) == '/') || ((*p_2->xml) == '>'))
      {
        {
          parseatt = 0;
          programStep = 22;
        }
      }
      else
      {
        programStep = 58;
      }
    }
    if (programStep == 58)
    {
      if (!(((((*p_2->xml) == ' ') || ((*p_2->xml) == '\t')) || ((*p_2->xml) == '\r')) || ((*p_2->xml) == '\n')))
      {
        programStep = 59;
      }
      else
      {
        programStep = 84;
      }
    }
    if (programStep == 59)
    {
      
      attname = p_2->xml;
      attnamelen = 0;
      programStep = 60;
    }
    if (programStep == 60)
    {
      if (((*p_2->xml) != '=') && (!(((((*p_2->xml) == ' ') || ((*p_2->xml) == '\t')) || ((*p_2->xml) == '\r')) || ((*p_2->xml) == '\n'))))
      {
        programStep = 61;
      }
      else
      {
        programStep = 64;
      }
    }
    if (programStep == 61)
    {
      attnamelen++;
      programStep = 62;
    }
    if (programStep == 62)
    {
      p_2->xml++;
      programStep = 63;
    }
    if (programStep == 63)
    {
      if (p_2->xml >= p_2->xmlend)
      {
        {
          parseatt = -1;
          programStep = 22;
        }
      }
      else
      {
        programStep = 60;
      }
    }
    if (programStep == 64)
    {
      if ((*(p_2->xml++)) != '=')
      {
        programStep = 65;
      }
      else
      {
        programStep = 66;
      }
    }
    if (programStep == 65)
    {
      if (p_2->xml >= p_2->xmlend)
      {
        {
          parseatt = -1;
          programStep = 22;
        }
      }
      else
      {
        programStep = 64;
      }
    }
    if (programStep == 66)
    {
      if (((((*p_2->xml) == ' ') || ((*p_2->xml) == '\t')) || ((*p_2->xml) == '\r')) || ((*p_2->xml) == '\n'))
      {
        programStep = 67;
      }
      else
      {
        programStep = 69;
      }
    }
    if (programStep == 67)
    {
      p_2->xml++;
      programStep = 68;
    }
    if (programStep == 68)
    {
      if (p_2->xml >= p_2->xmlend)
      {
        {
          parseatt = -1;
          programStep = 22;
        }
      }
      else
      {
        programStep = 66;
      }
    }
    if (programStep == 69)
    {
      sep = *p_2->xml;
      programStep = 70;
    }
    if (programStep == 70)
    {
      if ((sep == '\'') || (sep == '\"'))
      {
        programStep = 71;
      }
      else
      {
        programStep = 78;
      }
    }
    if (programStep == 71)
    {
      p_2->xml++;
      programStep = 72;
    }
    if (programStep == 72)
    {
      if (p_2->xml >= p_2->xmlend)
      {
        {
          parseatt = -1;
          programStep = 22;
        }
      }
      else
      {
        programStep = 73;
      }
    }
    if (programStep == 73)
    {
      attvalue = p_2->xml;
      attvaluelen = 0;
      programStep = 74;
    }
    if (programStep == 74)
    {
      if ((*p_2->xml) != sep)
      {
        programStep = 75;
      }
      else
      {
        programStep = 83;
      }
    }
    if (programStep == 75)
    {
      attvaluelen++;
      programStep = 76;
    }
    if (programStep == 76)
    {
      p_2->xml++;
      programStep = 77;
    }
    if (programStep == 77)
    {
      if (p_2->xml >= p_2->xmlend)
      {
        {
          parseatt = -1;
          programStep = 22;
        }
      }
      else
      {
        programStep = 74;
      }
    }
    if (programStep == 78)
    {
      attvalue = p_2->xml;
      attvaluelen = 0;
      programStep = 79;
    }
    if (programStep == 79)
    {
      if (((!(((((*p_2->xml) == ' ') || ((*p_2->xml) == '\t')) || ((*p_2->xml) == '\r')) || ((*p_2->xml) == '\n'))) && ((*p_2->xml) != '>')) && ((*p_2->xml) != '/'))
      {
        programStep = 80;
      }
      else
      {
        programStep = 83;
      }
    }
    if (programStep == 80)
    {
      attvaluelen++;
      programStep = 81;
    }
    if (programStep == 81)
    {
      p_2->xml++;
      programStep = 82;
    }
    if (programStep == 82)
    {
      if (p_2->xml >= p_2->xmlend)
      {
        {
          parseatt = -1;
          programStep = 22;
        }
      }
      else
      {
        programStep = 79;
      }
    }
    if (programStep == 83)
    {
      if (p_2->attfunc)
      {
        p->attfunc(p->data, attname, attnamelen, attvalue, attvaluelen);
      }
      else
      {
        
      }
      programStep = 84;
    }
    if (programStep == 84)
    {
      p_2->xml++;
      programStep = 56;
    }
    if (programStep == 85)
    {
      {
        parseatt = -1;
        programStep = 22;
      }
      programStep = 86;
    }
    if (programStep == 86)
    {
      {
        programStep = 22;
      }
    }
    if (programStep == 55)
    {
      {
        programStep = 3;
      }
    }
    if (programStep == 4)
    {
      run = 0;
    }
  }

}

