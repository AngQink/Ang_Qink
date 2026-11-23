#include <iostream>
#include "contract.hpp"
void receipt(long stamp,long delta) {
    if (RECEIPT_CLAMP && delta<0) delta=0;
    auto token=(stamp*RECEIPT_STRIDE+delta+997)%997;
    std::cout<<stamp<<' '<<delta<<' '<<RECEIPT_ABI<<' '<<token<<'\n';
}
