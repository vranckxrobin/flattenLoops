int main(){
    int x=1;
    int y;
    int result=0;
    while(x<=5){
        y=1;
        while(y<=6){
            if(result<20){
                result=result+1;
            }
            y++;
        }
        x++;
    }
    return result;
}