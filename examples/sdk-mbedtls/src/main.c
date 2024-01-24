#include <stdio.h>
#include <string.h>
#include "app_log.h"
#include <board_SK.h>
#include <mbedtls/ssl.h>
#include <mbedtls/aes.h>
#include <mbedtls/sha256.h>

int main(void)
{
    board_init();

    printf("\r\n");
    printf("************************************************************\r\n");
    printf("*                   mbedTLS example.                       *\r\n");
    printf("************************************************************\r\n");

    int ret;
    mbedtls_sha256_context ctx;
    uint8_t output_hash[32];
    const uint8_t data_to_hash[] = {
        'T', 'e', 's', 't'
    };
    mbedtls_sha256_init(&ctx);
    mbedtls_sha256_starts(&ctx, 0 /* is224 = false*/);
    ret = mbedtls_sha256_update_ret(&ctx, data_to_hash, sizeof(data_to_hash));
    if(ret) {
        printf("FAILED to update SHA256 hash.\n");
    }
    ret = mbedtls_sha256_finish_ret(&ctx, output_hash);
    if(ret) {
        printf("FAILED to finish SHA256 hash.\n");
    }
    mbedtls_sha256_free(&ctx);

    /* should output 532eaabd9574880dbf76b9b8cc00832c20a6ec113d682299550d7a6e0f345e25 */
    printf("Hash: ");
    for(int i=0; i< 32; i++) {
        printf("%02x", (unsigned) output_hash[i]);
    }
    printf("\n");
    
    while(1);
}
