# MobSF is used as the hardened analysis image because its static analyzer already
# bundles the Android analysis toolchain, including JADX/Apktool integrations.
FROM opensecurity/mobile-security-framework-mobsf:v4.5.3

USER root

COPY mobsf-scan /usr/local/bin/mobsf-scan
RUN chmod 0755 /usr/local/bin/mobsf-scan \
    && mkdir -p /work /tmp \
    && chown -R 9901:9901 /work

USER 9901
WORKDIR /work
ENTRYPOINT ["sleep", "infinity"]
