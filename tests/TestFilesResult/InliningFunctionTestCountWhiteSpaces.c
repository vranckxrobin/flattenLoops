#include "minixml.h"
#include <stdbool.h>
void parsexml(struct xmlparser *parser)
{
  bool run = 1;
  int programStep = 1;
  int parseatt;
  struct xmlparser *p;
  int counter = 0;
  while (run)
  {
    switch (programStep)
    {
      case 1:
        parser->xml = parser->xmlstart;
        programStep = 2;
        break;

      case 2:
        parser->xmlend = parser->xmlstart + parser->xmlsize;
        p = parser;
        programStep = 5;
        break;

      case 3:
        parseatt;
        programStep = 4;
        break;

      case 5:
        if (p->xml < (p->xmlend - 1))
      {
        programStep = 6;
      }
      else
      {
        programStep = 10;
      }
        break;

      case 6:
        if ((*p->xml) == ' ')
      {
        programStep = 7;
      }
      else
      {
        programStep = 9;
      }
        break;

      case 7:
        counter++;
        programStep = 8;
        break;

      case 8:
        p->xml++;
        programStep = 6;
        break;

      case 9:
        p->xml++;
        programStep = 5;
        break;

      case 10:
      {
        parseatt = counter;
        programStep = 3;
      }
        programStep = 11;
        break;

      case 11:
      {
        programStep = 3;
      }
        break;

      case 4:
        run = 0;
        break;

    }

  }

}

