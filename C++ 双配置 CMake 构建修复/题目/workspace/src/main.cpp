#include <iostream>
void receipt(long stamp,long delta);
int main() {
    for (long stamp,delta; std::cin>>stamp>>delta;) receipt(stamp,delta);
}
